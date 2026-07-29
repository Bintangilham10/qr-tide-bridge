import requests
import json
import time
from urllib.parse import urlparse, parse_qs
import re

class GoogleVerificationSimulator:
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id or "YOUR_GOOGLE_CLIENT_ID"
        self.client_secret = client_secret or "YOUR_GOOGLE_CLIENT_SECRET"
        self.device_verify_url = "https://accounts.google.com/o/oauth2/device/verify"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.user_agent = "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36"
    
    def parse_qr_payload(self, qr_data):
        """Parse Google OAuth device flow QR code - flexible version"""
        if not qr_data:
            return None
        
        result = {}
        
        # Case 1: Full URL with accounts.google.com
        try:
            parsed = urlparse(qr_data)
            if parsed.netloc in ['accounts.google.com', 'www.google.com']:
                query = parse_qs(parsed.query)
                for k, v in query.items():
                    result[k] = v[0] if isinstance(v, list) else v
                if 'user_code' in result or 'device_code' in result:
                    return result
        except:
            pass
        
        # Case 2: Raw query string (no URL)
        try:
            if '?' in qr_data:
                qs = qr_data.split('?')[1]
            else:
                qs = qr_data
            params = parse_qs(qs)
            for k, v in params.items():
                result[k] = v[0] if isinstance(v, list) else v
            if 'user_code' in result or 'device_code' in result:
                return result
        except:
            pass
        
        # Case 3: Key=value pairs separated by space or newline
        try:
            pairs = re.findall(r'(\w+)\s*[=:]\s*([^\s&]+)', qr_data)
            for k, v in pairs:
                result[k] = v
            if 'user_code' in result or 'device_code' in result:
                return result
        except:
            pass
        
        # Case 4: Raw text—return as 'raw_data' so frontend can show it
        return {'raw_data': qr_data}
    
    def simulate_device_verification(self, params):
        """Send verification request as if from mobile device"""
        headers = {
            'User-Agent': self.user_agent,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        data = {
            'client_id': params.get('client_id', self.client_id),
            'device_code': params.get('device_code', ''),
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
        }
        
        for attempt in range(30):
            try:
                response = requests.post(
                    self.token_url,
                    data=data,
                    headers=headers,
                    timeout=5
                )
                result = response.json()
                
                if 'access_token' in result:
                    return result
                if 'error' in result and result['error'] == 'authorization_pending':
                    time.sleep(10)
                    continue
                if 'error' in result:
                    return result
            except Exception:
                time.sleep(5)
                continue
        
        return {'error': 'timeout', 'error_description': 'Polling timed out'}