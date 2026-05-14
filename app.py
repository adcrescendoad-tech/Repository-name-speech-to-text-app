from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from google.cloud import speech_v1
from google.oauth2 import service_account
import os
import json
import io

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

@app.route('/', methods=['GET'])
def index():
    """index.html を配信"""
    try:
        # Docker 内のコンテナパス
        paths = [
            os.path.join(os.path.dirname(__file__), 'index.html'),
            os.path.join(os.path.dirname(__file__), 'static', 'index.html'),
            '/app/index.html',
            '/app/static/index.html'
        ]
        
        for path in paths:
            if os.path.exists(path):
                print(f"📄 Found index.html at: {path}")
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
        
        # ファイルが見つからない場合はエラー表示
        msg = f"❌ index.html not found. Tried: {', '.join(paths)}"
        print(msg)
        return f"<h1>{msg}</h1>", 404
        
    except Exception as e:
        print(f"❌ Error reading index.html: {e}")
        return f"<h1>Error: {str(e)}</h1>", 500

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
        print(f"❌ Transcribe error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
