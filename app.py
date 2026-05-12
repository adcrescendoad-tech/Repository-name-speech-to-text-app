from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import speech_v1
from google.oauth2 import service_account
import io
import base64
import os
import json

app = Flask(__name__)
CORS(app)

try:
    credentials_dict = json.loads(os.getenv('GOOGLE_CREDENTIALS_JSON'))
except (TypeError, json.JSONDecodeError):
    credentials_dict = {
        "type": "service_account",
        "project_id": "smooth-league-391605",
        "private_key_id": "6a1c347eb36526833de90a1449365af9d29f51eb",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDG9xV6aDTEtSoL\ns+OVEy4J1QXJcj14Wusw/FNORXbQ30ejt46LEW5uM2IctT9BRxxIROkoUlOxVVF1\nxgvCb1UJgnkc8zTRYUdzzApC5DyWxSmGM8dPVtxhIvjWHA5BMt80FaopAqcvfuWh\nausOBe7n4xbGxR94bwEZtMBhzzfTJWmbJhwlPpbImYPNGgCLAnAcqDw/NGrDAESU\nuLG69NqsoWqhtTk8v2YzlSmkxo9qbCI1ZJgDck1ROOugPUua83LdlR8y231MQ7Jj\nTgii90/VrIb9VGDv6jK+rVt/o3ncPQSKtUaKAAcWyI0UYpSNYKct83yGWQ6AUIcC\nKaz1EAS9AgMBAAECgf8RGSq/WjUusmLqnorwRLWwIp5csXSW4zlS/FwsXcvYJ1gA\nucWGLflPfxrvXKQS+Al2LHXdATYwByT4+gwIqYilSJEf68aeN73sNZysIvESA9+N\nqOV36/8EWf0IaWDQOY706ue0noW/jygstwN8MQZW5y0N5+LMdr2hd+cQgL5LZsS+\n17NDAdHNVsWyPa2rh9T3dscecouNXFQTc5dHHDNqs1Ww+9dbWuf/bx5ck9W9OP+j\nt3XIvzMTJfF8ovrBYX4CidCk2nQCkPjlqCqYJc/MDeZz8us12mfgX94XK7dbAzk2\n0MfcWBrfVyVwQ6oXg4Stxy3DtmM5cTz72Y8Vk0ECgYEA9ZSW8gRKpGCBoJwwUusR\nUi1MnGsROw3/5CzphaYBY6/BGKa95hs2J6vB0nKbP2SKC557L6fU8SLwKmwvb9Aa\n9x995gwz/gnZ8NxbFicQ9i5Zmuz6P/KvqHvEtxsxv3aSDifbziylNcVIKVJ1wyTg\njItqX14fKE+G+8bwUHsLZ/kCgYEAz2gs4xi40be0HPaT3TTIXfeNJK6bdYeNZvYB\nl/WFKwmpB5orTyrjRg+AiB5u1/mTr3dQ+c2R6eRrc/7CnQx4gtUB/NkPGB9HDZbm\nkng+t2MQoFftE3/h6n+lzYboVy6kOZDwzZYVZhIjFOAOh3IQRvCKxWOsfjLEKS6Q\nIw+62+UCgYEAx0TMvpCQ6JSOWn6iD4ZCRcYQFhQipSKU8tcmnZW4JuVj79bM3DxU\nUxhha5wnMOcpxIfSOTcb6JaK/kFOtJHOb5uUEujv/0CLIZAMMQt+DeRKPRXxcZZA\nxpu3YUSlt1BE70uUZdWAMQNlrHIGsFPqCODPbZb3/UOaqg4gzY0qEjECgYAMFTuY\nN1Z9EUCy90KB/pM1tjhIzMtNu4nnV6mcGreZXES2pqqjQBJhgIGybGN0vZt2+3KC\nOxGnGKGR7mOUFqfmp1YoTtTsSNYw2nuwSMUOlfzf+n9bRXX53VnhcVyTx6nVmLYO\npBG3EpNsoej2xxRfrZ/IBBiGeZqn84h+Imp2aQKBgQCsMiQep//W7OzssGFpP5iH\nxR/y5AsWGebHOEZ5fvQ9pH6PSsBwiO6HQKGGymuXnZTW2KQkvcLAl4BDwQx0KCVt\nvxW8gbiQdd3/h9d3D0v1oSQ95p9NEzVt158M8vk9Wzr5YA9kEmceyrWbUWWZuLqF\nXwmyXZTYrO3f+VrCjLRCww==\n-----END PRIVATE KEY-----\n",
        "client_email": "speech-to-text-api@smooth-league-391605.iam.gserviceaccount.com",
        "client_id": "112215722232215722200",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/speech-to-text-api%40smooth-league-391605.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }

credentials = service_account.Credentials.from_service_account_info(credentials_dict)
client = speech_v1.SpeechClient(credentials=credentials)

@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Speech to Text API is running!'})

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
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
    app.run(debug=False)
