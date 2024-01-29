"""from flask import Flask, request, jsonify
import uuid
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Beginning of DB code

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./our.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./our.db'

db = SQLAlchemy(app)

from sqldb import *

db.create_all()


# End of DB code

@app.route("/messages", methods=['POST'])
def save_message():
    if not request.method == "POST":
        return "", 405
    data = request.json
    message = data['message']
    message_id = str(uuid.uuid4())

    if len(message) > 140:
        return "", 400

    m = Messages(message=message, message_id=message_id)
    db.session.add(m)
    db.session.commit()

    return {'id': message_id}


@app.route("/messages/<MessageID>", methods=['GET'])
def get_message(MessageID):
    if not request.method == "GET":
        return "", 405
    if not MessageID:
        return "", 400
    message = Messages.query.filter_by(message_id=str(MessageID)).first()
    if message:
        return message.to_dict(), 200
    return "", 400


@app.route("/messages/<MessageID>", methods=['DELETE'])
def remove_message(MessageID):
    if not request.method == "DELETE":
        return "", 405
    if not MessageID:
        return "", 400
    message = Messages.query.filter_by(message_id=str(MessageID))
    if message:
        message.delete()
        db.session.commit()
        return "",200
    return "", 400


@app.route("/messages/<MessageID>/read/<UserId>", methods=['POST'])
def mark_read_message(MessageID, UserId):
    if not request.method == "POST":
        return "", 405
    message = Messages.query.filter_by(message_id=MessageID).first()
    u = User.query.filter_by(user_id=UserId).first()
    if not u:
        user = User(user_id=UserId)
    else:
        user = u
    if not message:
        return "", 400
    if MessageID and UserId:
        if not UserId in message.readBy:
            r = ReadBy()
            user.readMessages.append(r)
            message.readBy.append(r)
            db.session.commit()
        return "", 200
    else:
        return "", 400


@app.route("/messages", methods=['GET'])
def get_all_messages():
    if not request.method == "GET":
        return "", 405
    message_list = []
    messages = Messages.query.all()
    for message in messages:
        message_list.append(message.to_dict())
    return jsonify(message_list)


@app.route("/messages/unread/<UserId>", methods=['GET'])
def get_all_unread_messages(UserId):
    if not request.method == "GET":
        return "", 405
    if not UserId:
        return "", 400
    output = []
    messages = Messages.query.all()
    for message in messages:
        if not UserId in [x.user_id for x in message.readBy]:
            output.append(message.to_dict())
    return jsonify(output)



@app.errorhandler(404)
def page_not_found(e):
    return "", 404


if __name__ == "__main__":
    app.debug = True
    app.run(port=5000)
"""