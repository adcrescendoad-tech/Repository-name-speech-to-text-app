from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Test</title></head>
    <body>
        <h1>✅ Flask is working!</h1>
        <p>If you see this, the app is running.</p>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
