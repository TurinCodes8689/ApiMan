import streamlit as st
from streamlit.components.v1 import html
import random
import os
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient
from twilio.rest import Client
from datetime import datetime, timedelta, timezone
import pandas as pd # For usage statistics table
import re # Import the regular expression module

from langchain.chat_models import init_chat_model
from langchain.schema.messages import AIMessage, HumanMessage, SystemMessage


def zipper_interface():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ultra-Realistic 3D Zipper Interface</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
    <style>
        /* CSS RESET */
        html, body, div, span, applet, object, iframe,
        h1, h2, h3, h4, h5, h6, p, blockquote, pre,
        a, abbr, acronym, address, big, cite, code,
        del, dfn, em, img, ins, kbd, q, s, samp,
        small, strike, strong, sub, sup, tt, var,
        b, u, i, center,
        dl, dt, dd, ol, ul, li,
        fieldset, form, label, legend,
        table, caption, tbody, tfoot, thead, tr, th, td,
        article, aside, canvas, details, embed, 
        figure, figcaption, footer, header, hgroup, 
        menu, nav, output, ruby, section, summary,
        time, mark, audio, video {
            margin: 0;
            padding: 0;
            border: 0;
            font-size: 100%;
            font: inherit;
            vertical-align: baseline;
        }
        
        html, body {
            margin: 0 !important;
            padding: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            overflow: hidden !important;
            box-sizing: border-box !important;
            font-family: 'Montserrat', sans-serif;
            perspective: 1800px;
            background: #0a0a12;
            color: #f0f0f0;
        }

        /* MAIN CONTAINER */
        .main-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            background: radial-gradient(circle at center, #1a1a2e 0%, #0a0a12 100%);
        }

        /* ULTRA-REALISTIC ZIPPER TRACK */
        .zipper-track {
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 72px;
            height: 100vh;
            background: linear-gradient(90deg, 
                #3a3a3a 0%, 
                #4a4a4a 20%, 
                #5a5a5a 50%, 
                #4a4a4a 80%, 
                #3a3a3a 100%);
            box-shadow: 
                inset 0 0 30px rgba(0,0,0,0.8),
                0 0 50px rgba(0,0,0,0.6);
            z-index: 10;
            border-left: 2px solid rgba(255,255,255,0.1);
            border-right: 2px solid rgba(255,255,255,0.1);
        }

        .zipper-teeth {
            position: absolute;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(to right, 
                    transparent 0%, 
                    rgba(200,200,200,0.7) 2%, 
                    rgba(200,200,200,0.7) 48%, 
                    transparent 50%, 
                    transparent 52%, 
                    rgba(200,200,200,0.7) 53%, 
                    rgba(200,200,200,0.7) 98%, 
                    transparent 100%);
            background-size: 72px 40px;
            background-repeat: repeat-y;
            filter: drop-shadow(0 1px 1px rgba(0,0,0,0.5));
        }

        .zipper-track::before, .zipper-track::after {
            content: "";
            position: absolute;
            top: 0;
            width: 24px;
            height: 100%;
            background-repeat: repeat-y;
            background-size: 24px 40px;
            z-index: 2;
        }

        .zipper-track::before {
            left: 0;
            background-image: 
                linear-gradient(to right, 
                    rgba(220,220,220,0.9) 0%, 
                    rgba(180,180,180,0.9) 50%, 
                    transparent 50%);
            border-right: 1px solid rgba(255,255,255,0.3);
        }

        .zipper-track::after {
            right: 0;
            background-image: 
                linear-gradient(to left, 
                    rgba(220,220,220,0.9) 0%, 
                    rgba(180,180,180,0.9) 50%, 
                    transparent 50%);
            border-left: 1px solid rgba(255,255,255,0.3);
        }

        /* ZIPPER SLIDER - ULTRA REALISTIC */
        .zipper-slider {
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 140px;
            z-index: 100;
            cursor: grab;
            touch-action: none;
            filter: 
                drop-shadow(0 5px 15px rgba(0,0,0,0.5))
                drop-shadow(0 10px 30px rgba(0,0,0,0.3));
            transition: transform 0.1s ease-out;
        }

        .slider-body {
            position: absolute;
            width: 80px;
            height: 80px;
            top: 10px;
            left: 10px;
            background: linear-gradient(145deg, #6e6e6e, #4a4a4a);
            border-radius: 10px 10px 20px 20px;
            box-shadow: 
                inset 3px 3px 5px rgba(255,255,255,0.2),
                inset -3px -3px 5px rgba(0,0,0,0.5),
                0 10px 20px rgba(0,0,0,0.4);
            transform-style: preserve-3d;
            transform: rotateX(15deg);
        }

        .slider-top {
            position: absolute;
            width: 80px;
            height: 15px;
            top: 0;
            left: 0;
            background: linear-gradient(to bottom, #9d9d9d, #7a7a7a);
            border-radius: 10px 10px 0 0;
            box-shadow: 
                0 -2px 5px rgba(255,255,255,0.3),
                inset 0 -5px 10px rgba(0,0,0,0.2);
            transform-origin: bottom;
            transform: rotateX(-15deg);
        }

        .slider-bottom {
            position: absolute;
            width: 80px;
            height: 25px;
            bottom: -10px;
            left: 0;
            background: linear-gradient(to bottom, #5a5a5a, #3a3a3a);
            border-radius: 0 0 20px 20px;
            box-shadow: 
                inset 0 5px 10px rgba(0,0,0,0.4),
                0 5px 10px rgba(0,0,0,0.3);
        }

        .slider-pull {
            position: absolute;
            width: 60px;
            height: 80px;
            top: 60px;
            left: 20px;
            background: linear-gradient(to bottom, #8a8a8a, #6a6a6a);
            border-radius: 30px 30px 0 0;
            border: 3px solid #ccc;
            border-bottom: none;
            box-shadow: 
                0 -5px 15px rgba(0,0,0,0.4),
                inset 0 -10px 20px rgba(0,0,0,0.2);
            transform-origin: top;
            transform: rotateX(20deg);
            transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }

        .slider-pull.up {
            transform: rotateX(160deg);
            box-shadow: 
                0 10px 20px rgba(0,0,0,0.5),
                inset 0 10px 20px rgba(0,0,0,0.3);
        }

        .slider-pull-ring {
            position: absolute;
            width: 60px;
            height: 30px;
            bottom: -20px;
            left: -3px;
            background: linear-gradient(to bottom, #5a5a5a, #3a3a3a);
            border: 3px solid #ccc;
            border-top: none;
            border-radius: 0 0 30px 30px;
            box-shadow: 0 5px 10px rgba(0,0,0,0.3);
        }

        .slider-pull-ring::before {
            content: "";
            position: absolute;
            width: 40px;
            height: 20px;
            top: 5px;
            left: 10px;
            background: radial-gradient(ellipse at center, #7a7a7a 0%, #5a5a5a 70%, #3a3a3a 100%);
            border-radius: 50%;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        }

        .slider-hook {
            position: absolute;
            width: 20px;
            height: 40px;
            top: 30px;
            left: 40px;
            background: linear-gradient(to right, #7a7a7a, #5a5a5a);
            border-radius: 10px;
            border: 2px solid #ddd;
            box-shadow: 
                inset 0 0 10px rgba(0,0,0,0.5),
                0 3px 5px rgba(0,0,0,0.3);
            transform: rotateZ(-5deg);
        }

        /* SIDE PANELS WITH STUNNING CARDS */
        .side-panel {
            position: absolute;
            top: 0;
            width: calc(50vw - 36px);
            height: 100vh;
            background: linear-gradient(135deg, rgba(30, 30, 46, 0.95) 0%, rgba(42, 42, 58, 0.95) 100%);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 
                inset 0 0 50px rgba(0,0,0,0.5),
                0 0 100px rgba(0,0,0,0.7);
            z-index: 5;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem;
            box-sizing: border-box;
            overflow-y: auto;
            overflow-x: hidden;
            transform-style: preserve-3d;
            transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s ease;
        }

        .side-panel.left {
            left: 0;
            transform-origin: right center;
            border-right: none;
        }

        .side-panel.right {
            right: 0;
            transform-origin: left center;
            border-left: none;
        }

        /* SECTION HEADERS */
        .section-header {
            width: 100%;
            text-align: center;
            margin: 1rem 0 2rem 0;
            position: relative;
            padding-bottom: 1rem;
        }

        .section-header h2 {
            font-family: 'Playfair Display', serif;
            font-size: 2.5rem;
            font-weight: 700;
            color: #7b68ee;
            text-shadow: 0 2px 10px rgba(123, 104, 238, 0.4);
            letter-spacing: 1px;
            position: relative;
            display: inline-block;
        }

        .section-header h2::after {
            content: "";
            position: absolute;
            bottom: -10px;
            left: 25%;
            width: 50%;
            height: 3px;
            background: linear-gradient(90deg, transparent, #7b68ee, transparent);
            border-radius: 3px;
        }

        /* ULTRA-REALISTIC CARDS WITH ANIMATIONS */
        .card-container {
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2rem;
            perspective: 1000px;
        }

        .card {
            width: 90%;
            min-height: 180px;
            background: linear-gradient(135deg, rgba(40, 40, 60, 0.8) 0%, rgba(30, 30, 50, 0.9) 100%);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 
                0 10px 30px rgba(0, 0, 0, 0.3),
                inset 0 0 20px rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transform-style: preserve-3d;
            transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1);
            position: relative;
            overflow: hidden;
            opacity: 0;
            transform: translateY(50px) rotateX(10deg);
            will-change: transform, opacity;
        }

        .card::before {
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(
                45deg,
                transparent 0%,
                rgba(255, 255, 255, 0.03) 30%,
                rgba(255, 255, 255, 0.05) 50%,
                rgba(255, 255, 255, 0.03) 70%,
                transparent 100%
            );
            transform: rotate(45deg);
            transition: all 0.6s ease;
        }

        .card:hover {
            transform: translateY(-10px) scale(1.02) rotateX(0deg);
            box-shadow: 
                0 15px 40px rgba(0, 0, 0, 0.4),
                inset 0 0 30px rgba(255, 255, 255, 0.1);
        }

        .card:hover::before {
            left: 100%;
        }

        .card-header {
            font-family: 'Playfair Display', serif;
            font-size: 1.8rem;
            font-weight: 700;
            color: #9d86e9;
            margin-bottom: 1rem;
            position: relative;
            display: inline-block;
            text-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }

        .card-header::after {
            content: "";
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 50px;
            height: 2px;
            background: linear-gradient(90deg, #7b68ee, transparent);
            border-radius: 2px;
        }

        .card-content {
            font-size: 1.1rem;
            line-height: 1.6;
            color: rgba(240, 240, 240, 0.9);
            margin-top: 1rem;
        }

        .card-icon {
            position: absolute;
            top: 1.5rem;
            right: 1.5rem;
            width: 50px;
            height: 50px;
            background: rgba(123, 104, 238, 0.1);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: #7b68ee;
            box-shadow: 
                0 0 0 2px rgba(123, 104, 238, 0.3),
                inset 0 0 10px rgba(123, 104, 238, 0.2);
            transition: all 0.4s ease;
        }

        .card:hover .card-icon {
            transform: scale(1.1) rotate(10deg);
            box-shadow: 
                0 0 0 4px rgba(123, 104, 238, 0.4),
                inset 0 0 15px rgba(123, 104, 238, 0.3);
        }

        /* PARTICLE EFFECTS */
        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(255, 255, 255, 0.6);
            border-radius: 50%;
            pointer-events: none;
            z-index: 1;
        }

        /* CHATBOT IFRAME CONTAINER */
        .chatbot-container {
            position: absolute;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: #0a0a12;
            display: flex;
            justify-content: center;
            align-items: center;
            opacity: 0;
            pointer-events: none;
            z-index: 1;
            transition: opacity 0.8s cubic-bezier(0.23, 1, 0.32, 1);
        }

        .chatbot-container.revealed {
            opacity: 1;
            pointer-events: auto;
        }

        #chatbotIframe {
            width: 100%;
            height: 100%;
            border: none;
            background: transparent;
        }

        /* ANIMATION CLASSES */
        @keyframes float {
            0%, 100% { transform: translateY(0) rotateX(0deg); }
            50% { transform: translateY(-10px) rotateX(5deg); }
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
        }

        /* RESPONSIVE ADJUSTMENTS */
        @media (max-width: 768px) {
            .side-panel {
                width: calc(50vw - 20px);
                padding: 1rem;
            }
            
            .card {
                width: 95%;
                padding: 1.5rem;
            }
            
            .section-header h2 {
                font-size: 2rem;
            }
            
            .card-header {
                font-size: 1.5rem;
            }
            
            .card-content {
                font-size: 1rem;
            }
        }

        .animation-screen {
            position: absolute;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            opacity: 0;
            pointer-events: none;
            z-index: 1000;
            transition: opacity 1s ease;
        }
        
        .animation-screen.visible {
            opacity: 1;
            pointer-events: auto;
        }
        
        .title {
            font-size: 4rem;
            color: white;
            font-family: 'Playfair Display', serif;
            margin-bottom: 2rem;
            text-shadow: 0 0 20px rgba(123, 104, 238, 0.8);
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        .start-chat-btn {
            padding: 1rem 2rem;
            font-size: 1.5rem;
            background: linear-gradient(145deg, #7b68ee, #5f4bb6);
            color: white;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        
        .start-chat-btn:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.4);
        }
        
        @keyframes glow {
            from { text-shadow: 0 0 10px rgba(123, 104, 238, 0.8); }
            to { text-shadow: 0 0 20px rgba(123, 104, 238, 1), 0 0 30px rgba(123, 104, 238, 0.6); }
        }
        
    </style>
</head>
<body>
    <div class="main-container">
        <!-- Particle effects will be added here by JS -->
        
        <!-- Zipper Track -->
        <div class="zipper-track">
            <div class="zipper-teeth"></div>
        </div>
        
        <!-- Left Panel with Features -->
        <div class="side-panel left" id="leftPanel">
            <div class="section-header">
                <h2>Bot Features</h2>
            </div>
            <div class="card-container">
                <div class="card" data-delay="0.1">
                    <div class="card-icon">✨</div>
                    <h3 class="card-header">Feature 1</h3>
                    <p class="card-content">Advanced natural language processing for seamless interactions with contextual understanding and human-like responses.</p>
                </div>
                <div class="card" data-delay="0.3">
                    <div class="card-icon">⚡</div>
                    <h3 class="card-header">Feature 2</h3>
                    <p class="card-content">Real-time response generation powered by cutting-edge AI algorithms with near-zero latency.</p>
                </div>
                <div class="card" data-delay="0.5">
                    <div class="card-icon">🌐</div>
                    <h3 class="card-header">Feature 3</h3>
                    <p class="card-content">Multi-platform integration supporting web, mobile, and desktop environments with API access.</p>
                </div>
            </div>
        </div>
        
        <!-- Right Panel with Prospects -->
        <div class="side-panel right" id="rightPanel">
            <div class="section-header">
                <h2>Future Prospects</h2>
            </div>
            <div class="card-container">
                <div class="card" data-delay="0.2">
                    <div class="card-icon">🗣️</div>
                    <h3 class="card-header">Prospect 1</h3>
                    <p class="card-content">Expanding to support 50+ languages for global reach with regional dialect adaptation.</p>
                </div>
                <div class="card" data-delay="0.4">
                    <div class="card-icon">🎤</div>
                    <h3 class="card-header">Prospect 2</h3>
                    <p class="card-content">Deep integration with voice assistants (Alexa, Google Assistant, Siri) for hands-free operation.</p>
                </div>
                <div class="card" data-delay="0.6">
                    <div class="card-icon">📊</div>
                    <h3 class="card-header">Prospect 3</h3>
                    <p class="card-content">Advanced analytics dashboard with real-time metrics and user interaction insights.</p>
                </div>
            </div>
        </div>
        
        <!-- Zipper Slider -->
        <div class="zipper-slider" id="zipperSlider">
            <div class="slider-body"></div>
            <div class="slider-top"></div>
            <div class="slider-bottom"></div>
            <div class="slider-pull" id="sliderPull"></div>
            <div class="slider-pull-ring"></div>
            <div class="slider-hook"></div>
        </div>

        <!-- Chatbot Container -->
        <div class="chatbot-container" id="chatbotContainer">
            <iframe id="chatbotIframe" src="about:blank"></iframe>
        </div>

        <div class="animation-screen" id="animationScreen">
            <h1 class="title">Welcome to APIMAN</h1>
            <button class="start-chat-btn" id="startChatBtn">Start Chat</button>
        </div>
    </div>

    <script>
        // DOM Elements
        const zipperSlider = document.getElementById('zipperSlider');
        const sliderPull = document.getElementById('sliderPull');
        const leftPanel = document.getElementById('leftPanel');
        const rightPanel = document.getElementById('rightPanel');
        const zipperTrack = document.querySelector('.zipper-track');
        const chatbotContainer = document.getElementById('chatbotContainer');
        const chatbotIframe = document.getElementById('chatbotIframe');
        const cards = document.querySelectorAll('.card');
        const mainContainer = document.querySelector('.main-container');
        
        // State variables
        let isDragging = false;
        let startY = 0;
        let currentY = 0;
        let maxY = window.innerHeight - zipperSlider.offsetHeight;
        let momentum = 0;
        let lastY = 0;
        let deltaY = 0;
        let lastTime = 0;
        let particles = [];
        
        // Initialize particles
        function initParticles() {
            particles = []; // Clear existing particles
            for (let i = 0; i < 50; i++) {
                createParticle();
            }
        }
                
        function createParticle() {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            // Random position
            const x = Math.random() * window.innerWidth;
            const y = Math.random() * window.innerHeight;
            
            // Random size
            const size = Math.random() * 3 + 1;
            
            // Random opacity
            const opacity = Math.random() * 0.5 + 0.1;
            
            // Random animation
            const duration = Math.random() * 10 + 5;
            const delay = Math.random() * 5;
            
            particle.style.left = x + 'px';
            particle.style.top = y + 'px';
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            particle.style.opacity = opacity;
            particle.style.animation = 'float ' + duration + 's infinite ' + delay + 's';
            
            mainContainer.appendChild(particle);
            particles.push({
                element: particle,
                x: x,
                y: y,
                speed: Math.random() * 0.5 + 0.1,
                angle: Math.random() * Math.PI * 2,
                radius: Math.random() * 50 + 20
            });
        }

        // Update particles
        function updateParticles(time) {
            if (!particles || particles.length === 0) {
                requestAnimationFrame(updateParticles);
                return;
            }
            
            particles.forEach(particle => {
                if (!particle || !particle.element) return;
                
                particle.angle += particle.speed * 0.01;
                particle.x += Math.cos(particle.angle) * 0.2;
                particle.y += Math.sin(particle.angle) * 0.2;
                
                // Wrap around screen edges
                if (particle.x > window.innerWidth) particle.x = 0;
                if (particle.x < 0) particle.x = window.innerWidth;
                if (particle.y > window.innerHeight) particle.y = 0;
                if (particle.y < 0) particle.y = window.innerHeight;
                
                particle.element.style.left = `${particle.x}px`;
                particle.element.style.top = `${particle.y}px`;
            });
            
            requestAnimationFrame(updateParticles);
        }
        
        // Animate cards with staggered entrance
        function animateCards() {
            cards.forEach(card => {
                const delay = parseFloat(card.getAttribute('data-delay'));
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0) rotateX(0deg)';
                }, delay * 1000);
            });
        }
        
        // Handle drag start
        function handleDragStart(e) {
            isDragging = true;
            startY = e.clientY || e.touches[0].clientY;
            currentY = parseFloat(zipperSlider.style.top || '0');
            zipperSlider.style.cursor = 'grabbing';
            sliderPull.classList.remove('up');
            
            // Add active state to zipper
            zipperSlider.style.transform = 'translateX(-50%) scale(1.02)';
            
            document.addEventListener('mousemove', handleDrag);
            document.addEventListener('mouseup', handleDragEnd);
            document.addEventListener('touchmove', handleDrag, { passive: false });
            document.addEventListener('touchend', handleDragEnd);
        }
        
        // Handle dragging
        function handleDrag(e) {
            if (!isDragging) return;
            e.preventDefault();
            
            const clientY = e.clientY || e.touches[0].clientY;
            const now = performance.now();
            deltaY = clientY - (lastY || startY);
            lastY = clientY;
            
            if (lastTime) {
                const deltaTime = now - lastTime;
                if (deltaTime > 0) {
                    momentum = deltaY / deltaTime;
                }
            }
            lastTime = now;
            
            let newY = currentY + (clientY - startY);
            newY = Math.max(0, Math.min(newY, maxY));
            
            zipperSlider.style.top = `${newY}px`;
            updatePanels(newY);
        }
        
        // Handle drag end
        function handleDragEnd() {
            isDragging = false;
            lastY = 0;
            lastTime = 0;
            zipperSlider.style.cursor = 'grab';
            zipperSlider.style.transform = 'translateX(-50%) scale(1)';
            
            document.removeEventListener('mousemove', handleDrag);
            document.removeEventListener('mouseup', handleDragEnd);
            document.removeEventListener('touchmove', handleDrag);
            document.removeEventListener('touchend', handleDragEnd);
            
            // Apply momentum
            if (Math.abs(momentum) > 0.1) {
                applyMomentum();
            } else {
                checkSnapPosition();
            }
        }
        
        // Apply momentum after drag
        function applyMomentum() {
            const deceleration = 0.95;
            const threshold = 0.1;
            
            if (Math.abs(momentum) > threshold) {
                let currentTop = parseFloat(zipperSlider.style.top || '0');
                let newTop = currentTop + momentum * 20;
                
                newTop = Math.max(0, Math.min(newTop, maxY));
                
                zipperSlider.style.top = `${newTop}px`;
                updatePanels(newTop);
                
                momentum *= deceleration;
                requestAnimationFrame(applyMomentum);
            } else {
                checkSnapPosition();
            }
        }

        function showAnimationScreen() {
            const animationScreen = document.getElementById('animationScreen');
            animationScreen.classList.add('visible');
            
            
document.getElementById('startChatBtn').addEventListener('click', function() {
    const newURL = new URL(window.location.href);
    newURL.searchParams.set("start_chat", "true");
    window.location.href = newURL.toString();
});

        }

       // Modify the message listener to handle both zipper and chat actions
        window.addEventListener('message', function(event) {
            if (event.data.zipperOpen !== undefined) {
                window.parent.postMessage({'zipperOpen': event.data.zipperOpen}, '*');
            }
        });
        
        // Check if zipper should snap to open or closed position
        // Modify the checkSnapPosition function
        function checkSnapPosition() {
            const currentTop = parseFloat(zipperSlider.style.top || '0');
            const openThreshold = maxY * 0.7;
            
            if (currentTop >= openThreshold) {
                animateTo(maxY, () => {
                    sliderPull.classList.add('up');
                    zipperSlider.style.opacity = '0';
                    zipperSlider.style.pointerEvents = 'none';
                    zipperTrack.style.opacity = '0';
                    showAnimationScreen();
                });
            } else {
                animateTo(0, () => {
                    sliderPull.classList.remove('up');
                    zipperSlider.style.opacity = '1';
                    zipperSlider.style.pointerEvents = 'auto';
                    zipperTrack.style.opacity = '1';
                    document.getElementById('animationScreen').classList.remove('visible');
                    window.parent.postMessage(JSON.stringify({
                        zipperOpen: false
                    }), '*');
                });
            }
        }
        // Smooth animation to target position
        function animateTo(target, callback) {
            const start = parseFloat(zipperSlider.style.top || '0');
            const duration = 500; // ms
            const startTime = performance.now();
            
            function step(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const easeProgress = easeOutCubic(progress);
                const newTop = start + (target - start) * easeProgress;
                
                zipperSlider.style.top = `${newTop}px`;
                updatePanels(newTop);
                
                if (progress < 1) {
                    requestAnimationFrame(step);
                } else if (callback) {
                    callback();
                }
            }
            
            requestAnimationFrame(step);
        }
        
        // Easing function
        function easeOutCubic(t) {
            return 1 - Math.pow(1 - t, 3);
        }
        
        // Update panel positions based on zipper position
        function updatePanels(zipperTop) {
            const progress = zipperTop / maxY;
            
            // Calculate panel transformations
            const leftPanelX = -progress * 100;
            const rightPanelX = progress * 100;
            const panelRotateY = progress * 15;
            const panelSkewY = progress * 5;
            const panelOpacity = 1 - progress * 1.5;
            const panelScale = 1 - progress * 0.2;
            
            // Apply transformations
            leftPanel.style.transform = `
                translateX(${leftPanelX}vw) 
                rotateY(${panelRotateY}deg) 
                skewY(${-panelSkewY}deg) 
                scale(${panelScale})
            `;
            rightPanel.style.transform = `
                translateX(${rightPanelX}vw) 
                rotateY(${-panelRotateY}deg) 
                skewY(${panelSkewY}deg) 
                scale(${panelScale})
            `;
            
            leftPanel.style.opacity = panelOpacity;
            rightPanel.style.opacity = panelOpacity;
            
            // Update chatbot container opacity
            chatbotContainer.style.opacity = Math.min(1, progress * 1.5);
            
            // Update pull tab state
            if (progress > 0.1) {
                sliderPull.classList.add('up');
            } else {
                sliderPull.classList.remove('up');
            }
        }
        
        // Handle window resize
        function handleResize() {
            maxY = window.innerHeight - zipperSlider.offsetHeight;
            const currentTop = parseFloat(zipperSlider.style.top || '0');
            updatePanels(currentTop);
        }
        
        // Initialize
        function init() {
            maxY = window.innerHeight - zipperSlider.offsetHeight;
            zipperSlider.style.top = '0px';
            updatePanels(0);
            
            zipperSlider.addEventListener('mousedown', handleDragStart);
            zipperSlider.addEventListener('touchstart', handleDragStart, { passive: false });
            window.addEventListener('resize', handleResize);
            
            // Initialize animations
            initParticles();
            animateCards();
            // Don't call updateParticles() here - it's already called at the end of initParticles
            
            // Add floating animation to zipper
            zipperSlider.style.animation = 'float 4s ease-in-out infinite';
        }
        
        // Start everything when DOM is loaded
        document.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>
"""

def main():
    st.set_page_config(page_title="APIMAN - APIHub Chat Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
        <style>
            button[title="hidden"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

    
    st.markdown("""
        <style>
            .stApp {
                padding: 0 !important;
                margin: 0 !important;
                max-width: 100% !important;
            }
            .block-container {
                padding: 0 !important;
            }
            header[data-testid="stHeader"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'zipper_open' not in st.session_state:
        st.session_state.zipper_open = False
    if 'show_chat' not in st.session_state:
        st.session_state.show_chat = False

    # Listen for messages from the iframe
    st.markdown("""
        <script>
            window.addEventListener('message', function(event) {
                if (event.data === 'START_CHAT') {
                    window.streamlitAPI.setComponentValue('start_chat');
                }
                // Handle zipper open/close messages if needed
                if (event.data.zipperOpen !== undefined) {
                    window.streamlitAPI.setComponentValue('zipper:' + event.data.zipperOpen);
                }
            });
        </script>
    """, unsafe_allow_html=True)

    # Create a hidden component to receive messages
    query_params = st.experimental_get_query_params()
    if query_params.get("start_chat", [""])[0] == "true":
        st.session_state.show_chat = True
    elif value.startswith('zipper:'):
            st.session_state.zipper_open = value.split(':')[1] == 'true'
            st.rerun()

    # Main interface logic
    container = st.container()

    # Handle the component value updates
    component_value = st.empty()
    if component_value.button('hidden', key='component_listener'):
        value = st.session_state.get('component_listener', '')
        if value.startswith('zipper:'):
            st.session_state.zipper_open = value.split(':')[1] == 'true'
            st.rerun()
        elif value == 'action:start_chat':
            st.session_state.show_chat = True
            st.rerun()

    
    if not st.session_state.zipper_open:
        # Show the zipper interface
        with container:
            html(zipper_interface(), height=1200, scrolling=False)
            
            # Listen for zipper state changes
            zipper_state = st.empty()
            if zipper_state.button('hidden', key='zipper_state'):
                st.session_state.zipper_open = True
                st.rerun()
            
            st.markdown("""
                <script>
                    // Listen for zipper open events
                    window.addEventListener('message', function(event) {
                        if (event.data.zipperOpen === true) {
                            window.parent.document.querySelector('[data-testid="stMarkdownContainer"] iframe').contentWindow.postMessage({setZipperOpen: true}, '*');
                        }
                    });
                    
                    // Function to trigger Streamlit update
                    function setZipperOpen(value) {
                        const iframe = window.parent.document.querySelector('[data-testid="stMarkdownContainer"] iframe');
                        if (iframe) {
                            iframe.contentWindow.postMessage({setZipperOpen: value}, '*');
                        }
                    }
                </script>
            """, unsafe_allow_html=True)
    elif not st.session_state.show_chat:
        # Show empty container while animation screen is visible
        with container:
            html("", height=1)
            
            # Listen for show_chat message
            show_chat_state = st.empty()
            if show_chat_state.button('hidden', key='show_chat_state'):
                if 'show_chat:true' in st.session_state.get('show_chat_state', ''):
                    st.session_state.show_chat = True
                    st.rerun()
    else:
        # Show the bot interface
        with container:
            # THIS MUST BE THE VERY FIRST STREAMLIT COMMAND IN THE SCRIPT
            
            # --- Load Environment Variables ---
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

            
        #     # Add a button to return to zipper
        # if st.button("Return to Zipper Interface"):
        #     st.session_state.zipper_open = False
        #     st.rerun()

if __name__ == "__main__":
    main()