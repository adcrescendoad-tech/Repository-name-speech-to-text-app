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
import google.generativeai as genai

# ローカル開発用の環境変数(.env)を読み込む
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gemini API setting
gemini_api_key = os.environ.get('GEMINI_API_KEY')
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    logger.info("Gemini API configured successfully.")
else:
    logger.warning("GEMINI_API_KEY not found. Generative AI features will be disabled.")

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
        
        parsed_data = {}
        if gemini_api_key and transcript.strip():
            try:
                prompt = f"""
以下の音声認識されたテキストを解析し、社労士の相談助言記録票の各項目に該当する情報を抽出してJSON形式で返してください。
JSONのキーは以下の通りにしてください。該当する情報がない場合は空文字列を設定してください。

- companyName (企業名: ③名称)
- contactPerson (面接者の役職氏名: ⑦面接者の役職氏名)
- motivation (訪問のきっかけ: 「特別な指導・相談」「定期的な相談」「その他」のいずれかを選択、不明なら空文字)
- method (相談・助言実施方法: 「訪問」「電話」「オンライン」「メール」のいずれかを選択、不明なら空文字)
- laborStructure (①労働構造: 「一般労働者が多い」「高齢者の構成比が高い」「混在している」のいずれかを選択、不明なら空文字)
- laborStructureDetail (具体的な状況 - 労働構造: 人数など)
- recruitment (②採用状況: 「採用を実施している」「採用を実施していない」「その他」のいずれかを選択、不明なら空文字)
- recruitmentDetail (具体的な状況 - 採用状況: 募集職種や人数など)
- seniorEmployment (③高齢者の活用: 「活用できている」「あまり活用できていない」「活用できていない」のいずれかを選択、不明なら空文字)
- seniorEmploymentDetail (具体的な状況 - 高齢者の活用: 業務内容など)
- employmentMeasures (雇用確保措置: 「未実施企業」「実施中企業」「実施済み企業」のいずれかを選択、不明なら空文字)
- issues (課題: 特定された課題)
- advice (助言内容: 提供した助言)
- conclusion (結論: 「できるだけ早い機会に再訪問が必要」「具体的な支援が可能」「更なる改善が期待できる」「先駆的に取り組んでいる」「当面さらなる改善は期待できない」のいずれかを選択、不明なら空文字)
- conclusionReason (所見理由: 判断の根拠)

音声テキスト:
{transcript}
"""
                model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
                ai_response = model.generate_content(prompt)
                parsed_data = json.loads(ai_response.text)
                logger.info("Gemini parsing successful")
            except Exception as e:
                logger.error(f"Gemini API error: {e}")

        return jsonify({'success': True, 'transcript': transcript, 'parsed_data': parsed_data}), 200
        
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
