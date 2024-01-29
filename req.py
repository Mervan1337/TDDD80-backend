import requests
#url = "https://codrrip.herokuapp.com/"
url = "http://localhost:5000/"


def reg_user(username, email ,password):
    rreq = requests.post(url+"register", json={"username":username,"password":password,"email":email})
    print(rreq.json())


def login_user(email ,password):
    rreq = requests.post(url+"login", json={"password":password,"email":email})
    print(rreq.json())
    token = rreq.json()['access-token']
    header = {"Authorization": "Bearer " + token}
    print(rreq.json())
    print(token)
    return header


def logout_user(header):
    rreq = requests.post(url+"logout", headers=header)
    print(rreq.json())

def get_users(header):
    rreq = requests.get(url + "users", headers=header)
    for u in rreq.json():
        print(str(u)+"\n")

def look_profile(header):
    rreq  = requests.post(url+"profile", headers=header)
    print(rreq.json())

def like_user(user, header):
    rreq = requests.post(url+"user/like", headers=header, json={"target":user})
    print(rreq)

def unlike_user(user, header):
    rreq = requests.delete(url+"chat/delete", headers=header, json={"target":user})
    print(rreq)

def send_message(chat, message, header):
    rreq = requests.post(f"{url}chat/{chat}/message", headers=header, json={'message':message})
    print(rreq.content)

def get_chats(header):
    rreq = requests.post(url+"user/chats",headers=header)
    print(rreq.json())
    return rreq.json()

def get_chat_messages(chat, header):
    rreq = requests.post(url+"chat/"+chat, headers=header)
    return rreq.json()


def reg_log_users():
    reg_user("Louumi","k13@gmail.com", "0066")
    reg_user("Madie", "k12@gmail.com", "0066")
    h1 = login_user("k13@gmail.com", "0066")
    like_user("Madie", h1)
    h2 = login_user("k12@gmail.com", "0066")
    like_user("Louumi", h2)
    get_users(h2)

def fake_new_profiles(quant):
    for i in range(len(quant)):
        reg_user(f"fake{i}", f"hejfake@gmail.com{i}", "hej")

def real_log():
    reg_user("Louumi", "k13@gmail.com", "0066")
    h1 = login_user("k13@gmail.com", "0066")
    get_chats(h1)

#reg_log_users()

real_log()