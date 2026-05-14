from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import speech_v1
from google.oauth2 import service_account
import os
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

try:
    creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON', '{}')
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    client = speech_v1.SpeechClient(credentials=credentials)
    print("✅ Google Speech-to-Text API: 準備完了")
except Exception as e:
    print(f"⚠️ Google 認証エラー: {e}")
    client = None

@app.route('/transcribe', methods=['POST', 'OPTIONS'])
def transcribe():
    if request.method == 'OPTIONS':
        return '', 200
    
    file = request.files['file']
    audio_data = file.read()
    audio = speech_v1.RecognitionAudio(content=audio_data)
    config = speech_v1.RecognitionConfig(
        encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code='ja-JP',
        enable_automatic_punctuation=True,
    )
    response = client.recognize(config=config, audio=audio)
    transcript = ' '.join([result.alternatives[0].transcript for result in response.results if result.alternatives])
    return jsonify({'success': True, 'transcript': transcript})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
