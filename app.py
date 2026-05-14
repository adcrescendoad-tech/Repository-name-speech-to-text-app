from flask import Flask, send_from_directory
from flask_cors import CORS
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
CORS(app)

@app.route('/')
def index():
    try:
        return send_from_directory('static', 'index.html')
    except Exception as e:
        logger.error(f'Error: {e}')
        return {'error': str(e)}, 500

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
