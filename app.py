from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import speech_v1
from google.oauth2 import service_account
import os
import json

app = Flask(__name__)
CORS(app)

# Environment Variable から認証情報を読み込む
credentials_dict = None
try:
    creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if creds_json:
        print(f"DEBUG: GOOGLE_CREDENTIALS_JSON found, length: {len(creds_json)}")
        credentials_dict = json.loads(creds_json)
        print(f"DEBUG: Credentials loaded successfully")
    else:
        print("DEBUG: GOOGLE_CREDENTIALS_JSON not found in environment")
except Exception as e:
    print(f"DEBUG: Error loading credentials: {e}")

# Google Cloud Speech クライアントを初期化
client = None
if credentials_dict:
    try:
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        client = speech_v1.SpeechClient(credentials=credentials)
        print("DEBUG: Speech Client initialized successfully")
    except Exception as e:
        print(f"DEBUG: Error initializing Speech Client: {e}")

@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Speech to Text API is running!'})

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        if not client:
            return jsonify({
                'success': False,
                'error': 'Speech Client is not initialized. Check credentials.'
            }), 500
        
        if 'file' not in request.files:
            return jsonify({'error': 'ファイルが見つかりません'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'ファイル名が空です'}), 400
        
        audio_data = file.read()
        audio = speech_v1.RecognitionAudio(content=audio_data)
        
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="ja-JP",
            enable_automatic_punctuation=True,
        )
        
        response = client.recognize(config=config, audio=audio)
        transcript = ""
        for result in response.results:
            if result.alternatives:
                transcript += result.alternatives[0].transcript + " "
        
        return jsonify({
            'success': True,
            'transcript': transcript.strip()
        })
    except Exception as e:
        print(f"DEBUG: Error in /transcribe: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
