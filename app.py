from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from google.cloud import speech_v1
from google.oauth2 import service_account
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

GOOGLE_PROJECT_ID = '112157322322172200'
GOOGLE_SERVICE_ACCOUNT = 'speech-to-text-api@smooth-league-391605.iam.gserviceaccount.com'

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

speech_client = None

def init_google_client():
    global speech_client
    try:
        creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        if creds_json:
            try:
                creds_dict = json.loads(creds_json)
                credentials = service_account.Credentials.from_service_account_info(creds_dict)
                speech_client = speech_v1.SpeechClient(credentials=credentials)
                logger.info('✅ Google Speech-to-Text クライアント初期化成功')
                return True
            except Exception as e:
                logger.warning(f'環境変数パース失敗: {e}')
        
        creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if creds_path and os.path.exists(creds_path):
            credentials = service_account.Credentials.from_service_account_file(creds_path)
            speech_client = speech_v1.SpeechClient(credentials=credentials)
            logger.info('✅ ファイル認証成功')
            return True
        
        logger.warning('❌ 認証設定なし')
        return False
    except Exception as e:
        logger.error(f'❌ エラー: {e}')
        return False

@app.route('/')
def index():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(base_dir, 'index.html')
    logger.info(f'Loading index from: {index_path}')
    logger.info(f'File exists: {os.path.exists(index_path)}')
    logger.info(f'CWD: {os.getcwd()}')
    logger.info(f'Files in dir: {os.listdir(base_dir)}')
    with open(index_path, 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'ファイルが選択されていません', 'success': False}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'ファイルが選択されていません', 'success': False}), 400

        allowed_extensions = {'.m4a', '.mp3', '.wav', '.flac', '.ogg', '.webm'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'対応形式: {", ".join(allowed_extensions)}', 'success': False}), 400

        logger.info(f'処理開始: {file.filename}')
        file_content = file.read()
        logger.info(f'ファイルサイズ: {len(file_content) / (1024 * 1024):.2f} MB')

        transcript = transcribe_with_google(file_content, file.filename)

        if not transcript:
            return jsonify({'error': 'トランスクリプション取得失敗', 'success': False, 'transcript': '[処理失敗]'}), 500

        return jsonify({'success': True, 'transcript': transcript, 'status': 'completed', 'filename': file.filename}), 200

    except Exception as e:
        logger.error(f'エラー: {str(e)}')
        return jsonify({'error': f'エラー: {str(e)}', 'success': False}), 500

def transcribe_with_google(audio_content, filename):
    try:
        if not speech_client:
            logger.error('クライアント未初期化')
            return None

        file_ext = os.path.splitext(filename)[1].lower()
        encoding_map = {
            '.m4a': speech_v1.RecognitionConfig.AudioEncoding.MP3,
            '.mp3': speech_v1.RecognitionConfig.AudioEncoding.MP3,
            '.wav': speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            '.flac': speech_v1.RecognitionConfig.AudioEncoding.FLAC,
            '.ogg': speech_v1.RecognitionConfig.AudioEncoding.OGG_OPUS,
        }
        
        encoding = encoding_map.get(file_ext, speech_v1.RecognitionConfig.AudioEncoding.LINEAR16)
        config = speech_v1.RecognitionConfig(encoding=encoding, language_code='ja-JP', enable_automatic_punctuation=True)
        audio = speech_v1.RecognitionAudio(content=audio_content)

        try:
            response = speech_client.recognize(config=config, audio=audio)
        except Exception as e:
            operation = speech_client.long_running_recognize(config=config, audio=audio)
            response = operation.result(timeout=300)

        transcript_list = []
        for result in response.results:
            if result.alternatives:
                transcript_list.append(result.alternatives[0].transcript)

        return ' '.join(transcript_list).strip() or None

    except Exception as e:
        logger.error(f'Google API エラー: {str(e)}')
        return None

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Server is running', 'google_api': 'connected' if speech_client else 'not configured', 'project_id': GOOGLE_PROJECT_ID}), 200

if __name__ == '__main__':
    logger.info('🚀 研修レポート作成アプリ サーバー起動')
    if init_google_client():
        logger.info('✅ Google Speech-to-Text API: 準備完了')
    else:
        logger.warning('⚠️ Google Speech-to-Text API: 未設定')
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
