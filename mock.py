import hashlib
import time
import secrets
import base64

class MockVerification:
    def __init__(self):
        self.mock_secret = "TIDEGAP_MOCK_SALT_2026"
    
    def generate_fake_token(self, user_code):
        timestamp = int(time.time())
        hour_seed = int(timestamp / 3600)
        
        raw = f"{user_code}:{hour_seed}:{self.mock_secret}"
        hash_digest = hashlib.sha256(raw.encode()).hexdigest()
        
        token_prefix = "ya29"
        token_body = base64.urlsafe_b64encode(
            hash_digest[:32].encode()
        ).decode()[:40]
        
        return {
            'access_token': f"{token_prefix}.{token_body}",
            'token_type': 'Bearer',
            'expires_in': 3600,
            'scope': 'email profile',
            'refresh_token': f"1//{hash_digest[:20]}"
        }
    
    def generate_verified_session(self, email_domain="test"):
        user_code = secrets.token_hex(8).upper()
        token = self.generate_fake_token(user_code)
        token['session_id'] = hashlib.md5(f"{user_code}:{time.time()}".encode()).hexdigest()
        token['user_code'] = user_code
        token['mock'] = True
        return token