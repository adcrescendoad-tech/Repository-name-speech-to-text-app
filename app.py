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
        # 現在のディレクトリを確認
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"📁 Current directory: {current_dir}")
        print(f"📂 Files in /app: {os.listdir('/app')}")
        
        index_path = os.path.join(current_dir, 'index.html')
        print(f"🔍 Looking for index.html at: {index_path}")
        
        if os.path.exists(index_path):
            print(f"✅ Found index.html at: {index_path}")
            with open(index_path, 'r', encoding='utf-8') as f:
                return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
        else:
            print(f"❌ index.html NOT found at: {index_path}")
            return f"<h1>❌ index.html not found at {index_path}</h1><p>Files: {os.listdir(current_dir)}</p>", 404
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
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
