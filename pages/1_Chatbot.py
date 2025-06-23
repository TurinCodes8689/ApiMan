import os
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient
from twilio.rest import Client
from datetime import datetime, timedelta, timezone
import pandas as pd
import re
from langchain.chat_models import init_chat_model
from langchain.schema.messages import AIMessage, HumanMessage, SystemMessage

st.set_page_config(
    page_title="APIMAN - APIHub Chat Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID") or st.secrets.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN") or st.secrets.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER") or st.secrets.get("TWILIO_NUMBER")
SUPPORT_PHONE_NUMBER = os.getenv("SUPPORT_PHONE_NUMBER") or st.secrets.get("SUPPORT_PHONE_NUMBER")
MONGO_URI = os.getenv("MONGODB_URI") or st.secrets.get("MONGODB_URI")

if not SUPPORT_PHONE_NUMBER:
    st.error("Configuration Error: SUPPORT_PHONE_NUMBER environment variable not set.")
    st.stop()
if not GROQ_API_KEY:
    st.error("Configuration Error: GROQ_API_KEY is not set.")
    st.stop()
if not MONGO_URI:
    st.error("Configuration Error: MONGODB_URI is not set.")
    st.stop()
if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_NUMBER:
    st.warning("Warning: Twilio credentials not fully configured.")

try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client["apiman"]
    tickets_collection = db["support_tickets"]
    api_keys_collection = db["user_api_keys"]
except Exception as e:
    st.error(f"Database Connection Failed: {e}")
    st.stop()

@st.cache_resource
def get_chat_model():
    try:
        return init_chat_model(
            model="llama3-8b-8192",
            model_provider="groq",
            api_key=GROQ_API_KEY,
            temperature=0
        )
    except Exception as e:
        st.error(f"AI Model Initialization Failed: {e}")
        st.stop()

chat_model = get_chat_model()

def send_whatsapp_notification(ticket_id, title, description, contact_info=""):
    try:
        twilio_rest_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message_body = f"""
New Support Ticket #{ticket_id}

Title: {title}

Description:
{description}

Contact: {contact_info if contact_info else 'Not provided'}

Opened at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        twilio_rest_client.messages.create(
            body=message_body,
            from_="whatsapp:" + TWILIO_NUMBER,
            to="whatsapp:" + SUPPORT_PHONE_NUMBER
        )
    except Exception as e:
        st.warning(f"Failed to send WhatsApp notification. Error: {e}")

def create_support_ticket(title, description, contact_info="anonymous user"):
    ticket_data = {
        "title": title,
        "description": description,
        "contact": contact_info,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_updated": datetime.now(timezone.utc).isoformat()
    }
    try:
        result = tickets_collection.insert_one(ticket_data)
        ticket_id = str(result.inserted_id)
        send_whatsapp_notification(ticket_id, title, description, contact_info)
        return ticket_id
    except Exception as e:
        st.error(f"Failed to create support ticket. Error: {e}")
        return None

def store_api_key(user_id, api_key):
    try:
        api_keys_collection.update_one(
            {"user_id": user_id},
            {"$set": {"api_key": api_key, "updated_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )
        return True
    except Exception as e:
        st.error(f"Failed to store API key. Error: {e}")
        return False

def get_user_api_keys(user_id):
    try:
        records = api_keys_collection.find({"user_id": user_id})
        return [record["api_key"] for record in records] if records else []
    except Exception as e:
        st.error(f"Failed to retrieve API keys. Error: {e}")
        return []

def get_open_tickets():
    try:
        open_tickets = list(tickets_collection.find({"status": "open"}).sort("created_at", -1))
        return open_tickets
    except Exception as e:
        st.error(f"Failed to fetch open tickets. Error: {e}")
        return []


SYSTEM_PROMPT = """
You are APIMAN, an advanced, highly intelligent, and helpful chatbot exclusively for APIHub. Your purpose is to assist users with APIHub-related questions and provide accurate, concise information about our APIs.
Role: APIMAN is the dedicated chatbot for APIHub, specializing in API-related queries. Maintain a professional, friendly, and precise tone.

Scope of Expertise
Only answer questions about these APIHub services:

Image API
Endpoints: /postimg, /getyourimage, /getimagetotext, /reset-your-post
Functions: Upload, retrieve, search, delete images.

Video API
Endpoint: /getvideo
Function: Fetch video links by name/title.

Ecommerce API
Endpoints: /createproduct, /getallproduct, /deleteproduct
Functions: CRUD operations for product data.

QR Code Generator API
Endpoint: /qrcodegenerator
Function: Generate QR codes from text/URLs.

Weather API
Endpoint: /getweatherdata
Function: Fetch weather data by city name.

Profile Photo API
Endpoint: /namedphoto
Function: Generate profile pictures from initials.

Jokes API
Endpoint: /jokesapi
Function: Fetch random jokes.

Response Rules
1. Greetings/Introduction (Respond politely, DO NOT create ticket):
   - "Hi", "Hello", "Hey" → "Hello! I'm APIMAN, your APIHub assistant. How can I help with our APIs today?"
   - "Who are you?" → "I'm APIMAN, the dedicated assistant for APIHub services. Ask me about our APIs, endpoints, or authentication!"

2. On-Topic Questions (Answer clearly):
   - Endpoints, authentication (keys/tokens), rate limits, errors, data formats.
   - Example: "How do I authenticate with the Image API?" → Explain auth process.

3. Off-Topic/Unclear Questions → Create Support Ticket:
   - "How do I reset my password?" → "I cannot resolve this. A support ticket will be created."
   - "Tell me about cats." → "I specialize in APIs. A support ticket will be created for this query."

4. Code/Docs Requests: Direct users to relevant API sections or provide concise examples.

Tone & Fallback
- Friendly but professional: Avoid slang; use clear, technical language.
- Uncertainty: If unsure, say: "Let me check... A support ticket will be created for further assistance."
"""
def _get_recent_tickets_markdown():
    markdown_output = "### Recent Support Tickets\n"
    try:
        recent_tickets_data = get_open_tickets()
        if recent_tickets_data:
            ticket_records = []
            for t in recent_tickets_data:
                subject = t["title"].split('\n')[0]
                if len(subject) > 50:
                    subject = subject[:47] + "..."
                ticket_records.append({
                    "ID": str(t["_id"])[-6:],
                    "Subject": subject,
                    "Status": t["status"].capitalize(),
                    "Created": datetime.fromisoformat(t["created_at"]).strftime("%Y-%m-%d %H:%M")
                })
            recent_tickets_df = pd.DataFrame(ticket_records)
            markdown_output += recent_tickets_df.to_markdown(index=False)
        else:
            markdown_output += "No open tickets found in the database.\n"
    except Exception as e:
        markdown_output += f"Could not load recent tickets: {e}\n"
    return markdown_output

def _get_api_stats_markdown():
    markdown_output = "### API Usage Statistics\n"
    markdown_output += "Insights into your API consumption (mock data):\n\n"
    markdown_output += "**Total Requests (24h):** 1,245,678\n"
    markdown_output += "**Avg Latency (ms):** 75\n\n"
    markdown_output += "#### Daily Request Volume\n"
    chart_data = pd.DataFrame(
        {
            "Date": pd.to_datetime(pd.date_range(end=datetime.now(), periods=7, freq='D')),
            "Requests": [1500, 1800, 2200, 1900, 2500, 2300, 2700],
        }
    )
    markdown_output += "```\n"
    markdown_output += "Date          Requests\n"
    markdown_output += "----------  ----------\n"
    for index, row in chart_data.iterrows():
        markdown_output += f"{row['Date'].strftime('%Y-%m-%d')}  {row['Requests']}\n"
    markdown_output += "```\n"
    return markdown_output

def _get_contact_info_markdown():
    markdown_output = "### APIHUB Contact Info\n"
    markdown_output += "- whatsapp community: https://chat.whatsapp.com/J8iljiMAZcvB58RS9GYwjH\n"
    markdown_output += "- discord community: https://discord.com/invite/Fj28zvaz\n"
    markdown_output += "- linkedin: https://www.linkedin.com/in/apihub/\n\n"
    markdown_output += "### APIMAN Contact Info\n"
    markdown_output += "- email: apimancompany@gmail.com\n"
    return markdown_output

def _get_api_key_help_markdown():
    markdown_output = "### API Key Management\n"
    markdown_output += "To get your API key, visit: [APIHub Key Dashboard](https://www.apihub.digital/dashboard/getkey)\n\n"
    markdown_output += "You can store your API key here for future reference:\n"
    
    with st.expander("Store Your API Key"):
        user_id = st.text_input("Enter your User ID/Email")
        api_key = st.text_input("Enter your API Key", type="password")
        if st.button("Save API Key"):
            if api_key and user_id:
                if store_api_key(user_id, api_key):
                    st.success("API Key stored successfully!")
                else:
                    st.error("Failed to store API Key")
            else:
                st.warning("Please provide both User ID and API Key")
    
    return markdown_output

def _get_user_api_keys_markdown(user_id):
    markdown_output = "### Your API Keys\n"
    try:
        api_keys = get_user_api_keys(user_id)
        if api_keys:
            for idx, key in enumerate(api_keys, 1):
                markdown_output += f"{idx}. `{key[:4]}...{key[-4:]}`\n"
        else:
            markdown_output += "No API keys found for your account.\n"
        markdown_output += "\nTo get a new API key, visit: [APIHub Key Dashboard](https://www.apihub.digital/dashboard/getkey)\n"
    except Exception as e:
        markdown_output += f"Error retrieving API keys: {e}\n"
    return markdown_output

def render_manual_ticket_form():
    st.subheader("Manual Support Ticket")
    with st.form("ticket_form", clear_on_submit=True):
        subject = st.text_input("Subject of your Issue", key="manual_subject")
        details = st.text_area("Full Description", height=150, key="manual_details")
        contact = st.text_input("Your Contact Email / Username", value="", key="manual_contact")

        col1, col2 = st.columns([1, 1])
        with col1:
            submit_ticket_button = st.form_submit_button("Submit New Ticket")
        with col2:
            back_to_chat_button = st.form_submit_button("Back to Chat")

        if submit_ticket_button:
            if not (subject and details):
                st.warning("Please provide both a Subject and a Full Description for the ticket.")
            else:
                new_ticket_id = create_support_ticket(subject, details, contact if contact else "anonymous")
                if new_ticket_id:
                    st.success(f"Ticket #{new_ticket_id} submitted successfully!")
                    st.session_state.show_manual_form = False
                    st.session_state.chat_history.append({"role": "assistant", "content": f"Manual ticket #{new_ticket_id} has been created. Our team will get back to you shortly."})
                    st.rerun()
        elif back_to_chat_button:
            st.session_state.show_manual_form = False
            st.rerun()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --gemini-dark-bg: #0A0A0A;
        --gemini-card-bg: #151515;
        --gemini-text-color: #E8E8E8;
        --gemini-subtle-text: #B0B0B0;
        --gemini-accent-blue: #63B3ED;
        --gemini-accent-teal: #81E6D9;
        --gemini-gradient-blue: linear-gradient(145deg, #63B3ED, #4299E1);
        --gemini-gradient-teal: linear-gradient(145deg, #81E6D9, #4FD1C5);
        --gemini-shadow-dark: rgba(0, 0, 0, 0.7);
        --gemini-shadow-light: rgba(0, 0, 0, 0.4);
        --gemini-border-color: #383838;
        --gemini-input-bg: #202020;
        --submit-button-green: linear-gradient(145deg, #4CAF50, #2E8B57);
        --submit-button-green-hover: linear-gradient(145deg, #2E8B57, #4CAF50);
        --cancel-button-red: linear-gradient(145deg, #FF6B6B, #E53E3E);
        --cancel-button-red-hover: linear-gradient(145deg, #E53E3E, #FF6B6B);
    }

    .stApp {
        background: var(--gemini-dark-bg);
        color: var(--gemini-text-color);
        font-family: 'Inter', sans-serif;
    }

    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 20px;
        padding: 20px;
        overflow-y: auto;
        max-height: 480px;
        border: 1px solid var(--gemini-border-color);
        border-radius: 20px;
        background-color: var(--gemini-card-bg);
        box-shadow: inset 0 0 15px rgba(0,0,0,0.6);
    }

    .chat-message {
        display: flex;
        align-items: flex-start;
        font-size: 1rem;
        margin-bottom: 0;
    }

    .chat-message-user {
        justify-content: flex-end;
        align-self: flex-end;
        text-align: right;
    }

    .chat-message-assistant {
        justify-content: flex-start;
        align-self: flex-start;
        text-align: left;
    }

    .chat-avatar {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        flex-shrink: 0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.4);
    }

    .user-avatar {
        background: var(--gemini-gradient-blue);
        color: white;
        margin-left: 18px;
    }

    .assistant-avatar {
        background: var(--gemini-gradient-teal);
        color: var(--gemini-dark-bg);
        margin-right: 18px;
    }

    .message-bubble {
        padding: 15px 22px;
        border-radius: 25px;
        max-width: 70%;
        box-shadow: 0 5px 15px rgba(0,0,0,0.4);
        word-wrap: break-word;
    }

    .chat-message-user .message-bubble {
        background: linear-gradient(145deg, #00008B, #1A1A5A);
        color: white;
        border-bottom-right-radius: 8px;
    }

    .chat-message-assistant .message-bubble {
        background: var(--gemini-card-bg);
        color: var(--gemini-text-color);
        border: 1px solid var(--gemini-border-color);
        border-bottom-left-radius: 8px;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: var(--gemini-input-bg);
        color: var(--gemini-text-color);
        border: 1px solid #4A5568;
        border-radius: 15px;
        padding: 14px 20px;
        font-size: 1.05rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>APIMAN: Your APIHub Assistant</h1>", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "show_success_alert" not in st.session_state:
    st.session_state.show_success_alert = False
if "success_ticket_id" not in st.session_state:
    st.session_state.success_ticket_id = None
if "show_error_alert" not in st.session_state:
    st.session_state.show_error_alert = False
if "show_manual_form" not in st.session_state:
    st.session_state.show_manual_form = False
if "show_api_key_help" not in st.session_state:
    st.session_state.show_api_key_help = False
if "show_api_keys" not in st.session_state:
    st.session_state.show_api_keys = False
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = ""

main_col = st.columns([1])[0]

with main_col:
    if st.session_state.show_manual_form:
        render_manual_ticket_form()
    elif st.session_state.show_api_key_help:
        st.subheader("API Key Management")
        if st.button("Back to Chat"):
            st.session_state.show_api_key_help = False
            st.rerun()
        _get_api_key_help_markdown()
    elif st.session_state.show_api_keys:
        st.subheader("Your API Keys")
        if st.button("Back to Chat"):
            st.session_state.show_api_keys = False
            st.rerun()
        st.session_state.current_user_id = st.text_input("Enter your User ID/Email to view your API keys")
        if st.session_state.current_user_id:
            st.markdown(_get_user_api_keys_markdown(st.session_state.current_user_id))
    else:
        st.subheader("Chat with APIMAN")
        st.markdown('<div id="chat-history-scroll-area" class="chat-container">', unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                    <div class="chat-message chat-message-user">
                        <div class="message-bubble">
                            <strong>You:</strong> {msg['content']}
                        </div>
                        <div class="chat-avatar user-avatar">U</div>
                    </div>
                    """, unsafe_allow_html=True)
            elif msg["role"] == "assistant":
                clean_md = re.sub(r"</?div[^>]*>", "", msg["content"], flags=re.IGNORECASE)
                st.markdown("""
                    <div class="chat-message chat-message-assistant">
                        <div class="chat-avatar assistant-avatar">A</div>
                        <div class="message-bubble">
                """, unsafe_allow_html=True)
                st.markdown(clean_md, unsafe_allow_html=False)
                st.markdown("""
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
            <script>
                var chatHistoryDiv = document.getElementById('chat-history-scroll-area');
                if (chatHistoryDiv) {
                    chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
                }
            </script>
        """, unsafe_allow_html=True)

        user_input = st.chat_input("Ask APIMAN about APIHub or type 'show help' for commands...", key="chat_input")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.show_success_alert = False
            st.session_state.show_error_alert = False
            st.rerun()

        if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
            current_user_query = st.session_state.chat_history[-1]["content"].lower().strip()
            bot_response_content = ""

            if "show recent support tickets" in current_user_query or "show tickets" in current_user_query:
                bot_response_content = _get_recent_tickets_markdown()
            elif "show api usage statistics" in current_user_query or "show api stats" in current_user_query:
                bot_response_content = _get_api_stats_markdown()
            elif "show contact information" in current_user_query or "show contact" in current_user_query or "contact support" in current_user_query:
                bot_response_content = _get_contact_info_markdown()
            elif "apikey" in current_user_query or "api key" in current_user_query or "get api key" in current_user_query:
                bot_response_content = "You can get your API key here: [APIHub Key Dashboard](https://www.apihub.digital/dashboard/getkey)"
            elif "show api keys" in current_user_query or "my api keys" in current_user_query:
                st.session_state.show_api_keys = True
                st.rerun()
            elif "show help" in current_user_query or "commands" in current_user_query:
                bot_response_content = """
                ### APIMAN Commands:
                You can ask me to:
                - `show recent support tickets` or `show tickets`: See a list of your latest support tickets.
                - `show api usage statistics` or `show api stats`: Get an overview of your API consumption.
                - `show contact information` or `show contact`: Find ways to reach our support team.
                - `apikey` or `get api key`: Get your APIHub API key.
                - `create manual support ticket` or `new ticket`: Open a form to submit a detailed support ticket.
                - And of course, ask any question about APIHub endpoints, authentication, rate limits, errors, and data formats!
                """
            elif "create manual support ticket" in current_user_query or "new ticket" in current_user_query:
                st.session_state.show_manual_form = True
                st.session_state.chat_history.append({"role": "assistant", "content": "Alright, please fill out the details for your support ticket."})
                st.rerun()
            else:
                try:
                  
                    greetings = [
    "hi", "hello", "hey", "greetings", "hii", "hiii", "hiya", "heyy", "helloo", "hellooo",
    "good morning", "good afternoon", "good evening", "good night", "gm", "gn", "ga",
    "morning", "afternoon", "evening", "sup", "what's up", "wassup", "yo", "hola",
    "howdy", "ahoy", "salutations", "hi there", "hello there", "hey there",
    "greetings", "good day", "good to see you", "nice to see you", "long time no see",
    "how are you", "how's it going", "how's things", "what's new", "what's happening",
    "hi friend", "hello friend", "hey friend", "hiya", "how do you do", "hi hi",
    "hey hey", "hello hello", "hi again", "hello again", "hey again", "hiya", "heyo",
    "hi folks", "hello everyone", "hey all", "hi team", "hello team", "hey team",
    "hi sir", "hello sir", "hey sir", "hi ma'am", "hello ma'am", "hey ma'am",
    "hi pal", "hello pal", "hey pal", "hi buddy", "hello buddy", "hey buddy",
    "hi mate", "hello mate", "hey mate", "hi dude", "hello dude", "hey dude",
    "hiya", "heya", "howdy doody", "hi-ya", "hello-o", "hey-o", "hi-oh",
    "hi people", "hello people", "hey people", "hi guys", "hello guys", "hey guys",
    "hi folks", "hello folks", "hey folks", "hi y'all", "hello y'all", "hey y'all",
    "hi beautiful", "hello beautiful", "hey beautiful", "hi handsome", "hello handsome", "hey handsome",
    "hi stranger", "hello stranger", "hey stranger", "hi sunshine", "hello sunshine", "hey sunshine",
    "hi captain", "hello captain", "hey captain", "hi boss", "hello boss", "hey boss",
    "hi champ", "hello champ", "hey champ", "hi sport", "hello sport", "hey sport",
    "hi there", "hello there", "hey there", "hi you", "hello you", "hey you"
                          ]
                    introduction_questions = [
    "who are you", "what are you", "your name", "your purpose", "who is this",
    "what is your name", "what's your name", "who might you be", "who exactly are you",
    "what do you do", "what's your purpose", "what can you do", "what are your capabilities",
    "tell me about yourself", "describe yourself", "introduce yourself", "give me your intro",
    "who created you", "who made you", "who developed you", "who programmed you",
    "what are you called", "by what name are you called", "how should i call you",
    "what should i call you", "what do people call you", "what's your identity",
    "what's your function", "what's your job", "what's your role", "what's your mission",
    "what's your objective", "what's your goal", "what's your aim", "what's your task",
    "are you a bot", "are you a robot", "are you ai", "are you artificial intelligence",
    "are you human", "are you real", "are you a person", "are you a program",
    "what kind of bot are you", "what type of ai are you", "what sort of program are you",
    "what's your nature", "what's your essence", "what's your being", "what's your existence",
    "who are you really", "what are you exactly", "what exactly are you", "who exactly are you",
    "what's your deal", "what's your story", "what's your background", "what's your history",
    "what are you here for", "why do you exist", "why were you created", "why are you here",
    "what's your function", "what's your primary function", "what's your main purpose",
    "what do you specialize in", "what are you good at", "what can you help with",
    "what's your expertise", "what's your specialty", "what's your domain",
    "what's your focus", "what's your concentration", "what's your area",
    "what's your field", "what's your subject", "what's your topic",
    "what are you about", "what do you represent", "what do you stand for",
    "what's your brand", "what's your identity", "what's your character",
    "what's your personality", "what's your nature", "what's your disposition"
]
                    
                    current_user_query_lower = current_user_query.lower()
                    
                   
                    is_greeting = any(greet in current_user_query_lower for greet in greetings)
                    
                    
                    is_intro_question = any(q in current_user_query_lower for q in introduction_questions)
                    
                    if is_greeting:
                        bot_response_content = "Hello! I'm APIMAN, your APIHub assistant. How can I help with our APIs today?"
                    elif is_intro_question:
                        bot_response_content = "I'm APIMAN, the dedicated assistant for APIHub services. Ask me about our APIs, endpoints, or authentication!"
                    else:
                       
                        messages = [SystemMessage(content=SYSTEM_PROMPT)] + [
                            HumanMessage(content=msg["content"]) if msg["role"] == "user" else AIMessage(content=msg["content"])
                            for msg in st.session_state.chat_history[-5:]
                        ]
                        if not messages or messages[-1].content.lower().strip() != current_user_query or messages[-1].type != "human":
                             messages.append(HumanMessage(content=current_user_query))

                        llm_response = chat_model.invoke(messages).content
                        llm_response = re.sub(r'</\s*div\s*>', '', llm_response).strip()

                        api_related_keywords = [
                            "api", "endpoint", "authentication", "token", "key",
                            "image api", "video api", "ecommerce api", "qr code",
                            "weather api", "profile photo", "jokes api", "apihub",
                            "post", "get", "put", "delete", "request", "response",
                            "header", "body", "parameter", "query", "status code"
                        ]
                        
                        is_api_related = any(keyword in current_user_query_lower for keyword in api_related_keywords)

                        if not is_api_related:
                            ticket_title = "Non-API Question: " + (current_user_query[:50] + "..." if len(current_user_query) > 50 else current_user_query)
                            ticket_id_for_bot = create_support_ticket(ticket_title, current_user_query)
                            if ticket_id_for_bot:
                                bot_response_content = "I cannot resolve this. A support ticket has been created."
                                st.session_state.show_success_alert = True
                                st.session_state.success_ticket_id = ticket_id_for_bot
                            else:
                                bot_response_content = "I cannot resolve this. Please contact support directly."
                        else:
                            bot_response_content = llm_response

                except Exception as e:
                    ticket_title = "AI Chatbot Failure: " + (current_user_query[:30] + "..." if len(current_user_query) > 30 else current_user_query)
                    ticket_id_on_error = create_support_ticket(ticket_title, f"Error while processing: {current_user_query}\n\nError: {e}")
                    if ticket_id_on_error:
                        bot_response_content = "An error occurred. A support ticket has been created."
                        st.session_state.show_error_alert = True

            st.session_state.chat_history.append({"role": "assistant", "content": bot_response_content})
            st.rerun()
        if st.session_state.show_success_alert and st.session_state.success_ticket_id:
            st.success(f"Ticket #{st.session_state.success_ticket_id} created by APIMAN.")
        if st.session_state.show_error_alert:
            st.error("An error occurred. A support ticket has been created.")