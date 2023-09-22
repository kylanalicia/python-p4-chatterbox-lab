# imports
from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        # Return all messages ordered by created_at in ascending order
        messages = Message.query.order_by(Message.created_at.asc()).all()
        messages_serialized = [message.to_dict() for message in messages]
        return jsonify(messages_serialized)

    elif request.method == 'POST':
        # Create a new message with body and username from params
        data = request.get_json()
        body = data.get('body')
        username = data.get('username')

        if not body or not username:
            return jsonify({'message': 'Missing body or username in request'}), 400

        new_message = Message(body=body, username=username)
        db.session.add(new_message)
        db.session.commit()
        return jsonify(new_message.to_dict()), 201

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def message_by_id(id):
    message = Message.query.get(id)

    if not message:
        return jsonify({'message': 'Message not found'}), 404

    if request.method == 'PATCH':
        # Update the body of the message using params
        data = request.get_json()
        new_body = data.get('body')

        if not new_body:
            return jsonify({'message': 'Missing body in request'}), 400

        message.body = new_body
        db.session.commit()
        return jsonify(message.to_dict())

    elif request.method == 'DELETE':
        # Delete the message from the database
        db.session.delete(message)
        db.session.commit()
        return jsonify({'message': 'Message deleted'})

if __name__ == '__main__':
    app.run(port=5555)
