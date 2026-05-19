import os
import json
import logging
import io
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google.oauth2 import service_account
from google.cloud import speech_v1
from pydub import AudioSegment
from dotenv import load_dotenv

# ローカル開発用の環境変数(.env)を読み込む
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 環境変数からシークレットキー（JSON文字列）を取得
credentials = None
try:
    google_creds_json = os.environ.get('GCP_SECRET_KEY_JSON')
    if google_creds_json:
        creds_dict = json.loads(google_creds_json)
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        logger.info('Google Cloud Credentials successfully loaded from environment variable.')
    else:
        logger.warning('GOOGLE_CREDENTIALS_JSON environment variable not found. Testing mode or error will occur.')
except Exception as e:
    logger.error(f'Failed to load credentials: {e}')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if not credentials:
        return jsonify({'error': 'Google Cloud Credentials not configured on server.', 'success': False}), 500
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'ファイルがアップロードされていません', 'success': False}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'ファイルが選択されていません', 'success': False}), 400
            
        content = file.read()
        logger.info(f"Received file: {file.filename}, size: {len(content)} bytes")
        
        # pydubを使って音声をLINEAR16 wavフォーマットに変換
        audio = AudioSegment.from_file(io.BytesIO(content))
        wav_io = io.BytesIO()
        # 音声認識の精度を高めるため、モノラル（1チャンネル）で出力
        audio.set_channels(1).export(wav_io, format='wav')
        wav_data = wav_io.getvalue()
        
        client = speech_v1.SpeechClient(credentials=credentials)
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=audio.frame_rate,
            language_code='ja-JP'
        )
        audio_obj = speech_v1.RecognitionAudio(content=wav_data)
        
        # 音声認識を実行
        response = client.recognize(config=config, audio=audio_obj)
        
        transcript = ' '.join([alt.transcript for result in response.results for alt in result.alternatives])
        logger.info("Transcription successful")
        return jsonify({'success': True, 'transcript': transcript}), 200
        
    except Exception as e:
        logger.error(f'Transcription error: {e}')
        # 詳細なエラーログ出力
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    # ローカル実行時は 0.0.0.0 で起動
    app.run(host='0.0.0.0', port=port, debug=False)
