from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import json
from qr_extractor import QRExtractor
from simulator import GoogleVerificationSimulator
from mock import MockVerification
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    if 'qr_image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['qr_image']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(path)
    
    # Extract QR payload
    extractor = QRExtractor()
    qr_data = extractor.extract_from_image(path)
    
    # DEBUG: tampilkan isi QR di terminal
    print(f"[DEBUG] QR Payload: {qr_data}")
    
    if not qr_data:
        os.remove(path)
        return jsonify({
            'success': False,
            'error': 'No QR code detected in image'
        }), 400
    
    # Parse payload
    simulator = GoogleVerificationSimulator()
    params = simulator.parse_qr_payload(qr_data)
    
    # DEBUG: tampilkan hasil parse
    print(f"[DEBUG] Parsed params: {params}")
    
    if not params or params.get('raw_data'):
        os.remove(path)
        # Kirim balik data mentah biar user tahu isinya
        return jsonify({
            'success': False,
            'error': 'Invalid QR payload format',
            'raw_qr_data': qr_data[:500]  # potong biar nggak kepanjangan
        }), 400
    
    # Attempt real simulation first
    try:
        result = simulator.simulate_device_verification(params)
        if result.get('access_token'):
            os.remove(path)
            return jsonify({
                'success': True,
                'access_token': result['access_token'],
                'refresh_token': result.get('refresh_token'),
                'expires_in': result.get('expires_in', 3600),
                'token_type': result.get('token_type', 'Bearer'),
                'scope': result.get('scope', 'email')
            })
    except Exception as e:
        print(f"[DEBUG] Simulation error: {e}")
        # Fallback ke mock jika simulasi gagal
        mock = MockVerification()
        result = mock.generate_fake_token(params.get('user_code', 'unknown'))
        os.remove(path)
        return jsonify({
            'success': True,
            'mode': 'mock',
            'access_token': result['access_token'],
            'token_type': result['token_type'],
            'expires_in': result['expires_in'],
            'scope': result['scope'],
            'note': 'Mock token generated - not valid for production'
        })
    
    os.remove(path)
    return jsonify({
        'success': False,
        'error': result.get('error_description', 'Verification failed')
    }), 400

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'alive', 'version': '1.0.0'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)