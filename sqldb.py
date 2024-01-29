import uuid

from server import db
from server import bcrypt


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary Key
    user_id = db.Column(db.String(120), unique=True)
    likes = db.relationship('Like', lazy=True)
    favorites = db.relationship('Favorite', lazy=True)
    password = db.Column(db.String(200), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True)
    profile_pic = db.Column(db.String(120), unique=False)
    description = db.Column(db.String(1000), unique=False)
    chats = db.relationship("Chat",
                            primaryjoin="or_(Profile.user_id==Chat.user1_id,"
                                        "Profile.user_id==Chat.user2_id)")
    # chats = db.Column(db.String) # Json list string of all chats

    def __init__(self, user_id, password, email):
        self.user_id = user_id
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.email = email
        self.profile_pic = "default.png"
        self.description = ""

    def set_description(self, desc):
        self.description = desc

    def set_profile_pic(self, url):
        self.profile_pic = url

    def to_dict(self):
        result = {
            'user_id': self.user_id,
            'email': self.email,
            'mylikes': [x.liked_id for x in self.likes],
            'favorites': [f.fav_id for f in self.favorites],
            'pfp': self.profile_pic,
            'desc': self.description,
            'chats': [x.to_dict() for x in self.chats]
        }
        return result


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(120), unique = True)
    user1_id = db.Column(db.String(120), db.ForeignKey('profile.user_id')) # Will search both columns to get chat
    user2_id = db.Column(db.String(120), db.ForeignKey('profile.user_id'))
    user1 = db.relationship(Profile, foreign_keys=[user1_id])
    user2 = db.relationship(Profile, foreign_keys=[user2_id])
    messages = db.relationship('Message', lazy=True)

    def __init__(self):
        self.chat_id = uuid.uuid4().hex

    def to_dict(self):
        result = {
            'id':self.id,
            'chat_id':self.chat_id,
            'user1_id':self.user1_id,
            'user2_id':self.user2_id,
            'messages':[x.to_dict() for x in self.messages]
        }
        return result

    def add_message(self, message):
        self.messages.append(message)
    

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    chat_id = db.Column(db.String(120), db.ForeignKey('chat.chat_id'))
    message = db.Column(db.String(500))
    user_id = db.Column(db.String(120))
    read = db.Column(db.Boolean, default=False)

    def __init__(self, message, user_id):
        self.user_id = user_id
        self.message = message

    def to_dict(self):
        result = {
            'message': self.message,
            'user_id': self.user_id,
        }
        return result


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    user_id = db.Column(db.String(120), db.ForeignKey('profile.user_id'),
                           nullable=False)  # what message id has been read
    liked_id = db.Column(db.String(120))


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    user_id = db.Column(db.String(120), db.ForeignKey('profile.user_id'),
                        nullable=False)  # what message id has been read
    fav_id = db.Column(db.String(120))


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
