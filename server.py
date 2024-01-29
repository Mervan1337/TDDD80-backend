from operator import itemgetter

from flask import Flask, request, jsonify, render_template
import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import *
from flask_jwt_extended import *
from datetime import *
import os
import uuid

app = Flask(__name__)

# App configs

if 'NAMESPACE' in os.environ and os.environ['NAMESPACE'] == 'heroku':
    db_uri = os.environ['DATABASE_URL']
    if db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)
    debug_flag = False
else:  # when running locally: use sqlite
    db_path = os.path.join(os.path.dirname(__file__), 'our.db')
    db_uri = 'sqlite:///{}'.format(db_path)
    debug_flag = True

ACCESS_EXPIRES = timedelta(weeks=2)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['JWT_SECRET_KEY'] = SECRET_KEY #"PUT YOUR SECRET KEY HERE"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = ACCESS_EXPIRES 
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)
db.create_all()

# DB CODE IMPORT

from sqldb import *


#   PROFILE MEANS YOUR OWN PROFILE AS THE USER USING THE APP
#   USER MEANS ANOTHER USER E.G AN USER YOU SEE IN THE APP NOT CREATED BY THE PROFILE
#   MATCHES IS MADE BY A PROFILE AND USER HAS LIKED EACH OTHER WHICH CAN BE GATHERED BY THE ARRAY FROM THE DATABASE

#   Check Like

@app.route('/register', methods=['POST'])
def register_a_new_user():
    """ Creates a temporary user before checking if it already exists.
    If it exists, return a 404 error else return a successful database commit. """
    data = request.json
    username = data['username']
    given_password = data['password']
    email = data['email'].lower()
    temp_user = Profile.query.filter_by(user_id=username).first()
    temp_email = Profile.query.filter_by(email=email).first()
    if temp_user is not None:
        return jsonify(message="User already exists"), 404
    elif temp_email is not None:
        return jsonify(message="Email is already in use"), 404
    else:
        user = Profile(user_id=username, password=given_password, email=email)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User created"), 200


@app.route('/login', methods=['POST'])
def user_login():
    """ Takes in email and password, tries to log in if successful create an access token else return 400 error """
    data = request.json
    email = data['email'].lower()
    password = data['password']
    temp_user = Profile.query.filter_by(email=email).first()
    if temp_user is None:
        return jsonify(message="Wrong username or password!"), 400
    if bcrypt.check_password_hash(temp_user.password, password):
        return jsonify({'access-token': create_access_token(identity=temp_user.user_id)}), 200
    return jsonify(message="Wrong username or password"), 400


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    """ Checks if a token is revoked."""
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None


# Logs user out.
@app.route('/logout', methods=['POST'])
@jwt_required()
def modify_token():
    """ If trying to logout, ban the token from being able to reuse and append it in a block list. """
    jti = get_jwt()['jti']
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify(message="Logged out!"), 200


# Get your own profile info
@app.route("/profile", methods=["POST"])
@jwt_required()
def own_profile():
    """ Tries to gather your own profile
    If you are not logged in return a 404 error else return the profile with a 200 """
    user_id = get_jwt_identity()
    profile = Profile.query.filter_by(user_id=str(user_id)).first()


    if not profile:
        return "It looks like you don't exist", 404
    else:
        p_dict = profile.to_dict()
        favs = len(Favorite.query.filter_by(fav_id=str(user_id)).all())
        p_dict['fav_count'] = favs
        return jsonify(p_dict), 200
    # 202


# Get other user profile
@app.route("/user/<user_id>", methods=["GET"])
@jwt_required()
def other_profile(user_id):
    """ Tries to gather profile information, if the user doesn't exist return a 404 else return info with a 200"""
    user_id = get_jwt_identity()
    profile = Profile.query.filter_by(user_id=str(user_id)).first()

    if not profile:
        return "It looks like you don't exist", 404
    else:
        p_dict = profile.to_dict()
        favs = len(Favorite.query.filter_by(fav_id=str(user_id)).all())
        p_dict['fav_count'] = favs
        return jsonify(p_dict), 200

    ## 202


# Like user
@app.route("/user/like", methods=["POST"])
@jwt_required()
def like_user():
    """
    Firstly it gathers information about the user who likes where it gets user_id and user.
    Secondly it gathers same information about the target user. Then there is a controller checking if the targeted_user
    exists. If the target user doesn't exists, return a 400
    Else it will check if targeted user has liked the user or not, if it has it will start a chat between the two users.
    If not the user will get appended to targeted user like list.
    """
    data = request.json
    user_id = get_jwt_identity()
    user = Profile.query.filter_by(user_id=str(user_id)).first()
    target_user_id = data["target"]
    target_user = Profile.query.filter_by(user_id=str(target_user_id)).first()
    if target_user != None:
        target_likes = target_user.to_dict()['mylikes']
        if target_user_id not in user.to_dict()['mylikes']:
            like = Like(liked_id=str(target_user_id))
            user.likes.append(like)
        else:
            return "Already liked", 400
        if user_id in target_likes:
            chat = Chat()
            chat.user1 = user
            chat.user2 = target_user
            db.session.add(chat)
        db.session.commit()
        return "User liked", 200
    else:
        return "Target doesnt exist", 400


# Get chats
@app.route("/user/chats", methods=['POST'])
@jwt_required()
def get_chats():
    """ Claims info about the user then appends it in a chat_list. Returning all chats"""
    user_id = get_jwt_identity()
    u = Profile.query.filter_by(user_id=str(user_id)).first()
    chats = u.chats
    chats_list = []
    for chat in chats:
        user_dict = {}
        user_dict['id'] = chat.id
        user_dict['chat_id'] = chat.chat_id
        if chat.user1 == u:
            user_dict['user_id'] = chat.user2_id
        else:
            user_dict['user_id'] = chat.user1_id
        chats_list.append(user_dict)
    new_list = sorted(chats_list, key=itemgetter('id'))
    return jsonify(new_list), 200


# Get messages from chat_id

@app.route("/chat/<chat_id>", methods=['GET', 'POST'])
@jwt_required()
def get_chat_messages(chat_id):
    """ Gets a chat between two users but can also notify if read"""
    c = Chat.query.filter_by(chat_id=str(chat_id)).first()
    messages = c.messages
    message_list = []
    for message in messages:
        message.read = True
        message_list.append(message.to_dict())
    return jsonify(message_list),200


@app.route("/chat/<chat_id>/message", methods=['POST'])
@jwt_required()
def send_message_to_chat(chat_id):
    """ Puts a message in a conservation """

    message = request.headers.get("message")
    user_id = get_jwt_identity()
    chat = Chat.query.filter_by(chat_id=str(chat_id)).first()
    if chat and message:
        m = Message(message, user_id)
        chat.add_message(m)
        db.session.commit()
        return message + " sent", 200
    else:
        return f"{chat_id} doesnt exist or {message}", 400


@app.route("/user/setprof", methods=['POST'])
@jwt_required()
def set_description():
    """ Puts a description in your profile and sets your profile-picture (filename in the firebase) """
    desc = request.json['desc']
    pfp = request.json['pfp']
    user_id = get_jwt_identity()
    user = Profile.query.filter_by(user_id=str(user_id)).first()
    user.set_description(desc)
    user.set_profile_pic(pfp)
    db.session.commit()
    return desc + " set", 200

@app.route("/user/<user_id>/favorite", methods=['POST'])
@jwt_required()
def favorite_user(user_id):
    """ Favorites a user, checks if favorite:d before, if not it does not add another favorite to the list. """
    u_id = get_jwt_identity()
    u = Profile.query.filter_by(user_id=u_id).first()
    target_user = Profile.query.filter_by(user_id=user_id).first()
    if target_user:
        prim_user = Profile.query.filter_by(user_id=u_id).first()
        if user_id not in prim_user.to_dict()['favorites']:
            f = Favorite()
            f.fav_id = user_id
            u.favorites.append(f)
            db.session.commit()
            return "favorite added", 200
        else:
            return "Already a favorite", 200
    else:
        return "target doesnt exist", 400

@app.route("/users", methods=['GET'])
@jwt_required()
def get_all_users():
    """ Get all users in a feed. Not including the user who requested the list."""
    u_id = get_jwt_identity()
    u = Profile.query.filter_by(user_id=u_id).first()
    users = Profile.query.all()
    user_list = []
    for user in users:
        if user.user_id != u_id and user.user_id not in u.to_dict()['mylikes']:
            u_dict = user.to_dict()
            favs = len(Favorite.query.filter_by(fav_id=str(user.user_id)).all())
            u_dict['fav_count'] = favs
            user_list.append(u_dict)
    return jsonify(user_list), 200


@app.route("/chat/delete/<target>", methods=['DELETE'])
@jwt_required()
def delete_chat(target):
    """ Deletes a chat between two users but also removes the like. Returns a 200 when successful."""
    user_id = get_jwt_identity()
    # u = Profile.query.filter_by(user_id=user_id).first()
    like_id = target
    l = Like.query.filter_by(liked_id=like_id, user_id=user_id).first()
    l2 = Like.query.filter_by(liked_id=user_id, user_id=like_id).first()
    c = Chat.query.filter((Chat.user1_id == like_id and Chat.user2_id == user_id) or (
                Chat.user1_id == user_id and Chat.user2_id == like_id)).first()
    if l:
        db.session.delete(l)
    if l2:
        db.session.delete(l2)
    if c:
        db.session.delete(c)
    else:
        print(l, c)
    db.session.commit()
    return jsonify(["Supposedly went right"]), 200


@app.errorhandler(404)
def page_not_found(e):
    """ Returns 404 if you try to access a link which doesn't exists"""
    return "Page not found", 404


if __name__ == "__main__":
    app.debug = debug_flag
    app.run(port=5000)
