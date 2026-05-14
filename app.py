from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import speech_v1
from google.oauth2 import service_account
import os
import json

app = Flask(__name__)
CORS(app)

# Google 認証初期化
try:
    creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON', '{}')
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    client = speech_v1.SpeechClient(credentials=credentials)
    print("✅ Google Speech-to-Text API: 準備完了")
except Exception as e:
    print(f"⚠️ Google 認証エラー: {e}")
    client = None

@app.route('/')
def index():
    """index.html を配信（絶対パス使用）"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(base_dir, 'index.html')
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except FileNotFoundError:
        return f"<h1>Error: index.html not found at {index_path}</h1>", 404

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Google Speech-to-Text で音声ファイルをテキスト化"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'ファイルが見つかりません'}), 400
        
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'success': False, 'error': 'ファイルが選択されていません'}), 400
        
        audio_data = file.read()
        audio = speech_v1.RecognitionAudio(content=audio_data)
        
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code='ja-JP',
            enable_automatic_punctuation=True,
        )
        
        response = client.recognize(config=config, audio=audio)
        transcript = ' '.join([result.alternatives[0].transcript for result in response.results if result.alternatives])
        
        return jsonify({'success': True, 'transcript': transcript}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
