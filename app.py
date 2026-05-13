from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from google.cloud import speech_v1
from google.oauth2 import service_account
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Google Cloud 設定
GOOGLE_PROJECT_ID = '112157322322172200'
GOOGLE_SERVICE_ACCOUNT = 'speech-to-text-api@smooth-league-391605.iam.gserviceaccount.com'

# アップロード用の一時ディレクトリ
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Google Speech-to-Text クライアント初期化
speech_client = None

def init_google_client():
    """Google Speech-to-Text クライアント初期化"""
    global speech_client
    try:
        # 環境変数から認証情報を取得（JSON 文字列）
        creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        if creds_json:
            try:
                creds_dict = json.loads(creds_json)
                credentials = service_account.Credentials.from_service_account_info(creds_dict)
                speech_client = speech_v1.SpeechClient(credentials=credentials)
                logger.info('✅ Google Speech-to-Text クライアント初期化成功（環境変数から）')
                return True
            except Exception as e:
                logger.warning(f'環境変数の JSON パース失敗: {e}')
        
        # ファイルから認証情報を取得
        creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if creds_path and os.path.exists(creds_path):
            credentials = service_account.Credentials.from_service_account_file(creds_path)
            speech_client = speech_v1.SpeechClient(credentials=credentials)
            logger.info(f'✅ Google Speech-to-Text クライアント初期化成功（ファイルから: {creds_path}）')
            return True
        
        logger.warning('❌ Google 認証ファイルが見つかりません')
        return False
    
    except Exception as e:
        logger.error(f'❌ Google 認証初期化エラー: {e}')
        return False


@app.route('/')
def index():
    """index.html を配信"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')


@app.route('/transcribe', methods=['POST'])
def transcribe():
    """音声ファイルを Google Speech-to-Text API でトランスクリプション"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'ファイルが選択されていません', 'success': False}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'ファイルが選択されていません', 'success': False}), 400

        # ファイル形式チェック
        allowed_extensions = {'.m4a', '.mp3', '.wav', '.flac', '.ogg', '.webm'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                'error': f'対応形式: {", ".join(allowed_extensions)}',
                'success': False
            }), 400

        logger.info(f'📝 処理開始: {file.filename}')

        # ファイルをメモリに読み込み
        file_content = file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        logger.info(f'📦 ファイルサイズ: {file_size_mb:.2f} MB')

        # Google Speech-to-Text API でトランスクリプション
        logger.info('🔄 Google Speech-to-Text API で処理中...')
        transcript = transcribe_with_google(file_content, file.filename)

        if not transcript:
            logger.warning('⚠️ トランスクリプション取得失敗')
            return jsonify({
                'error': 'トランスクリプション取得失敗（API エラー）',
                'success': False,
                'transcript': '[処理失敗]'
            }), 500

        logger.info('✅ トランスクリプション完了')
        return jsonify({
            'success': True,
            'transcript': transcript,
            'status': 'completed',
            'filename': file.filename
        }), 200

    except Exception as e:
        logger.error(f'❌ エラー発生: {str(e)}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'エラー: {str(e)}',
            'success': False
        }), 500


def transcribe_with_google(audio_content, filename):
    """Google Speech-to-Text API を使用してトランスクリプション"""
    try:
        if not speech_client:
            logger.error('❌ Google Speech-to-Text クライアントが初期化されていません')
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

        config = speech_v1.RecognitionConfig(
            encoding=encoding,
            language_code='ja-JP',
            enable_automatic_punctuation=True,
            sample_rate_hertz=None,
        )

        audio = speech_v1.RecognitionAudio(content=audio_content)

        logger.info(f'🎤 API に送信中... ({len(audio_content)} bytes)')

        try:
            response = speech_client.recognize(config=config, audio=audio)
        except Exception as e:
            logger.warning(f'⚠️ recognize() 失敗: {e}')
            logger.info('💡 long_running_recognize を試行中...')
            operation = speech_client.long_running_recognize(config=config, audio=audio)
            response = operation.result(timeout=300)

        transcript_list = []
        for result in response.results:
            if result.alternatives:
                alt_text = result.alternatives[0].transcript
                logger.info(f'📌 認識結果: {alt_text}')
                transcript_list.append(alt_text)

        transcript = ' '.join(transcript_list).strip()
        
        if not transcript:
            logger.warning('⚠️ 空のトランスクリプション')
            return None

        logger.info(f'✅ 完了: {len(transcript)} 文字')
        return transcript

    except Exception as e:
        logger.error(f'❌ Google Speech-to-Text エラー: {str(e)}')
        import traceback
        traceback.print_exc()
        return None


@app.route('/health', methods=['GET'])
def health():
    """ヘルスチェック"""
    google_status = 'connected' if speech_client else 'not configured'
    return jsonify({
        'status': 'ok',
        'message': 'Server is running',
        'google_api': google_status,
        'project_id': GOOGLE_PROJECT_ID
    }), 200


if __name__ == '__main__':
    logger.info('=' * 60)
    logger.info('🚀 研修レポート作成アプリ サーバー起動')
    logger.info('=' * 60)
    logger.info(f'📍 Google Project ID: {GOOGLE_PROJECT_ID}')
    
    if init_google_client():
        logger.info('✅ Google Speech-to-Text API: 準備完了')
    else:
        logger.warning('⚠️ Google Speech-to-Text API: 未設定')
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
