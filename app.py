from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    """index.html を配信"""
    try:
        with open('/app/index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except FileNotFoundError:
        return "<h1>index.html not found</h1>", 404
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>", 500

@app.route('/transcribe', methods=['POST'])
def transcribe():
    return jsonify({'success': False, 'error': 'Not implemented'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
