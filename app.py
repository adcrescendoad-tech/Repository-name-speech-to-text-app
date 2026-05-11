from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import speech_v1
from google.oauth2 import service_account
import io
import base64
import os

app = Flask(__name__)
CORS(app)

credentials_dict = {
    "type": "service_account",
    "project_id": "smooth-league-391605",
    "private_key_id": "6005c6a65e9a25698861a4c377c279fe5df694f6",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDCKx60iTTJjyJn\nsdDcu9f8ilBBlVppYCEnD+TnT1PoB0dOkMCt/oNuHvfpJ73mYOvde6diN2GFH10Q\nt/6AofTgX8xVlendr0TddISozxmQX74hNGIb43hc91Gd4p1Bd+DtCvESrLk5yGtW\nWncqpZihOZsYa13ht9dx4EIkvMyvOFm+/+rmw16/t2fQOjMVTRIvyrf45/6YpXqf\nJzSaBiaJc7/A/lvWh1LfMkUomLQ1O4DTo1/K/ulhim6toxGW0MPb9dSKwvCQKo0I\nbkhhwYRpOCEt/ycd8HTScucMXHRbvd7+Fj5tbA9cFFxDwrcjhS6nohowmPxzOw7v\nD6e15O0jAgMBAAECggEAAzH/dtwdLMX4vHkeJUvIEaVbDcE99Cb7VK+7xhy1lkds\nYnwaV6KtGgZTcRhQ1TY6G3J5/jFIHw81kl1cyFQh+gFJlQz7BMVqHjTZLAgAdTJG\nKDi69peHNwxw4ObGTLoCzxPThMmn4K4OKiUh+ecwvFJ83WmC6YCDgKG+pOkgey+s\nXxWY4b/7MPcolz3PFkaA1IF6JpwKxbCLroxn9je3BBWa2ASubaIYhaw6d5kNk6Z5\n/UVbcOyT22K1uHRUUk7YGtJbDDsffU+0QArVVBlri1p079ppGB/PzJtE0m0rk1AL\nEjfo30bcG5lG7bZoQ/IwQlJzwJF8SSWbyEoXl9luLQKBgQDlimB/ztZIRnfdDBWD\nTbR2lGDcPbSeyDwSV33vQXBQ2JfJayMxJ65iglUADFPkZZvupgKNSydwLp6e9+zk\n58832XyquQKNdBCoI83O/mh9nDxPnXA94o0ruw7rkmCVXhzy5Wkwos4SOmaQZhxE\n8k9Kv+oF8kgNrOtqYqqtmZmkFQKBgQDYjO47a0Y7olkqEB/cgNbkPTmEXBbrF+cB\nPY1gu4Z4GOp1aoBEmZjuhM0Yhtd2g0wafJbNcqnVEY4lH3JXQiJTAJVw496ZXRf7\nB0M4PzWBkrW5/ebeL6kW6GAzkT9mxMBIQFIe9NA4IIT2ecH8X90vYp/3/e7vVi4w\n2zrfTU4CVwKBgQCjy8Dcsw45+P8jn7HiRprWWz9bKjUvcRdcx044Yuvw5P47XtZ4\nBybraLGbHTDoNJG3FIORq+VyqfHK4oQLPFekNPA/K1Jk+kPAl/wPD4Ak0k4/ScuE\nfZvbbtpQw91j+QqTUZ1kdWiznTT/Kb5WfMqUPqqSn7dG+vPqsIm243q9mQKBgH/L\ni7wdLrF6ucwNAACNOEQxrYPjJNNQo88jmA+CG3U8nwDz/QZ+7rW0QaU7zmPuUDdB\nV22fQYKwfYaC7GN6b+8z5P1ePLudKM3IF29WPildf0loAZsV3V/bewpzqUroyeDZ\ntJz4NPkql80tRcG+gTW5qlYb0aoE3fWPK0skv+i5AoGBAONwprjZ8EzLu1sM6Imu\nxV2S6N5dQ5nVvIUOE0uPrOb4TEGSTpJYtOjY2Ev0KVdgkp9hALW7BOwBxD/II4MV\n/R7+SCd4DugG6hOLYoangFAQPFgQdC2ioURuSkMg0tLLFA0iILu6wV3HMXTAf2YG\nBcVxxUsxym4KDscmrlurcq02\n-----END PRIVATE KEY-----\n",
    "client_email": "id-539@smooth-league-391605.iam.gserviceaccount.com",
    "client_id": "101077191055085505679",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/id-539%40smooth-league-391605.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

credentials = service_account.Credentials.from_service_account_info(credentials_dict)
client = speech_v1.SpeechClient(credentials=credentials)

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
