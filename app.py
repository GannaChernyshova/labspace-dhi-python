from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return """
    <h1>Hello, World!</h1>
    <p>This is a simple Python Flask application running in Docker.</p>
    <p><a href="/health">Check Health</a></p>
    """

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'Application is running successfully',
        'python_version': '3.13'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8888))
    app.run(host='0.0.0.0', port=port, debug=False) 