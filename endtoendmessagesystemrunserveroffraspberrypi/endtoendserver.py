from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
#users = {'user1': 'passwordforuser1', 'user2': 'passwordforuser2'}  # Example: {'username': 'hashed_password'}
users = {}  # Stores username: {password_hash, public_key}
messages = []

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    if username in users:
        return jsonify({'error': 'Username already exists'}), 409
    users[username] = {'password': generate_password_hash(password)}
    return jsonify({'message': 'Registration successful'}), 201

@app.route('/register_key', methods=['POST'])
def register_key():
    username = request.json['username']
    public_key = request.json['public_key']
    if username in users:
        users[username]['public_key'] = public_key
        return jsonify({'message': 'Public key registered successfully'}), 200
    return jsonify({'error': 'User not found'}), 404

@app.route('/get_public_key', methods=['POST'])
def get_public_key():
    username = request.json['username']
    if username in users and 'public_key' in users[username]:
        return jsonify({'public_key': users[username]['public_key']}), 200
    return jsonify({'error': 'Public key not found'}), 404

@app.route('/send', methods=['POST'])
def send_message():
    data = request.get_json()
    sender = data['sender']
    receiver = data['receiver']
    encrypted_message = data['encrypted_message']
    messages.append((sender, receiver, encrypted_message))
    return jsonify({'message': 'Message sent successfully'}), 200

@app.route('/receive', methods=['POST'])
def receive_message():
    receiver = request.get_json()['receiver']
    receiver_messages = [msg for msg in messages if msg[1] == receiver]
    return jsonify({'messages': receiver_messages}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
