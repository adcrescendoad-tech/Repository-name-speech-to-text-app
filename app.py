from flask import Flask, render_template_string, request, jsonify
import json
import os
from google.cloud import speech_v1
from google.oauth2 import service_account

app = Flask(__name__)

# Google Cloud Speech-to-Text の認証
def get_speech_client():
    """Google Speech-to-Text クライアントを取得"""
    creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if not creds_json:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS_JSON not set")
    
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    return speech_v1.SpeechClient(credentials=credentials)

# HTML テンプレート
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>音声認識アプリ</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 500px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        input[type="file"], input[type="text"], textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.3s;
        }
        input[type="file"]:focus, input[type="text"]:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        button {
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .btn-primary:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-secondary:hover {
            background: #5a6268;
        }
        .result-box {
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 15px;
            margin-top: 20px;
            display: none;
        }
        .result-box.show {
            display: block;
        }
        .result-box h3 {
            color: #333;
            margin-bottom: 10px;
        }
        .result-box p {
            color: #666;
            line-height: 1.6;
            word-wrap: break-word;
        }
        .loading {
            text-align: center;
            color: #667eea;
            font-weight: 500;
            display: none;
        }
        .loading.show {
            display: block;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 6px;
            margin-top: 10px;
            display: none;
        }
        .error.show {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ 音声認識アプリ</h1>
        
        <form id="uploadForm">
            <div class="form-group">
                <label for="audioFile">音声ファイルをアップロード (MP3, WAV, など)</label>
                <input type="file" id="audioFile" accept="audio/*" required>
            </div>
            
            <div class="form-group">
                <label for="language">言語コード (デフォルト: ja-JP)</label>
                <input type="text" id="language" value="ja-JP" placeholder="例: ja-JP, en-US">
            </div>
            
            <div class="button-group">
                <button type="submit" class="btn-primary">認識開始</button>
                <button type="reset" class="btn-secondary">クリア</button>
            </div>
        </form>
        
        <div class="loading" id="loading">
            ⏳ 音声を認識中... しばらくお待ちください
        </div>
        
        <div class="error" id="error"></div>
        
        <div class="result-box" id="resultBox">
            <h3>認識結果:</h3>
            <p id="resultText"></p>
            <button type="button" class="btn-primary" id="exportBtn" style="width: 100%; margin-top: 10px;">
                📊 Excel にエクスポート
            </button>
        </div>
    </div>

    <script>
        const form = document.getElementById('uploadForm');
        const audioFile = document.getElementById('audioFile');
        const languageInput = document.getElementById('language');
        const loadingDiv = document.getElementById('loading');
        const errorDiv = document.getElementById('error');
        const resultBox = document.getElementById('resultBox');
        const resultText = document.getElementById('resultText');
        const exportBtn = document.getElementById('exportBtn');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const file = audioFile.files[0];
            if (!file) return;

            // UI リセット
            errorDiv.classList.remove('show');
            resultBox.classList.remove('show');
            loadingDiv.classList.add('show');

            try {
                // ファイルを Base64 に変換
                const reader = new FileReader();
                reader.onload = async (event) => {
                    const base64Audio = event.target.result.split(',')[1];
                    const language = languageInput.value || 'ja-JP';

                    // サーバーに送信
                    const response = await fetch('/recognize', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            audio: base64Audio,
                            language: language
                        })
                    });

                    const data = await response.json();
                    loadingDiv.classList.remove('show');

                    if (data.success) {
                        resultText.textContent = data.text || '(認識結果なし)';
                        resultBox.classList.add('show');
                        
                        // グローバル変数に保存（Excel エクスポート用）
                        window.lastResult = {
                            text: data.text,
                            language: language,
                            timestamp: new Date().toLocaleString('ja-JP')
                        };
                    } else {
                        errorDiv.textContent = `エラー: ${data.error || '不明なエラー'}`;
                        errorDiv.classList.add('show');
                    }
                };
                reader.readAsDataURL(file);
            } catch (err) {
                loadingDiv.classList.remove('show');
                errorDiv.textContent = `エラー: ${err.message}`;
                errorDiv.classList.add('show');
            }
        });

        // Excel エクスポート
        exportBtn.addEventListener('click', () => {
            if (!window.lastResult) return;

            const ws_data = [
                ['認識結果'],
                ['テキスト', window.lastResult.text],
                ['言語', window.lastResult.language],
                ['実行日時', window.lastResult.timestamp]
            ];

            const ws = XLSX.utils.aoa_to_sheet(ws_data);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, 'Result');
            XLSX.writeFile(wb, `speech_recognition_${Date.now()}.xlsx`);
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/recognize', methods=['POST'])
def recognize():
    """Google Speech-to-Text API で音声認識"""
    try:
        data = request.get_json()
        audio_base64 = data.get('audio')
        language_code = data.get('language', 'ja-JP')

        if not audio_base64:
            return jsonify({'success': False, 'error': 'No audio provided'}), 400

        # Google Speech-to-Text API を呼び出し
        client = get_speech_client()
        
        audio = speech_v1.RecognitionAudio(content=bytes(audio_base64, 'utf-8'))
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.MP3,
            sample_rate_hertz=16000,
            language_code=language_code,
            enable_automatic_punctuation=True
        )

        response = client.recognize(config=config, audio=audio)
        
        # 結果を集約
        transcript = ''
        for result in response.results:
            for alternative in result.alternatives:
                transcript += alternative.transcript + ' '

        return jsonify({
            'success': True,
            'text': transcript.strip() or '(認識結果なし)'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
