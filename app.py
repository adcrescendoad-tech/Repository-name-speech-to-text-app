from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import speech_v1
from google.oauth2 import service_account
import os
import json

app = Flask(__name__)
CORS(app)

# Environment Variable から認証情報を読み込む
try:
    creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if creds_json:
        credentials_dict = json.loads(creds_json)
    else:
        raise ValueError("GOOGLE_CREDENTIALS_JSON is not set")
except Exception as e:
    print(f"Error loading credentials: {e}")
    credentials_dict = {}

# Google Cloud Speech クライアントを初期化
try:
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)
    client = speech_v1.SpeechClient(credentials=credentials)
except Exception as e:
    print(f"Error initializing Speech Client: {e}")
    client = None

@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Speech to Text API is running!'})

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        if not client:
            return jsonify({
                'success': False,
                'error': 'Speech Client is not initialized'
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
