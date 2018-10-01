from flask import Flask, request, redirect, url_for, render_template, make_response
from datetime import datetime, timedelta
from flask_socketio import SocketIO, send, emit, join_room, leave_room

import bcrypt
import time
import json
import html
import random
import string
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO()
socketio.init_app(app)

# User management
def create_user(username, password):
    assert not user_exists(username)

    pass_salt = bcrypt.gensalt()
    pass_hash = bcrypt.hashpw(str.encode(password), pass_salt)

    query = "INSERT INTO users (user, password_hash, password_salt, bandit_score) VALUES (?, ?, ?, 0)"
    with sqlite3.connect('data.db') as db:
        user = db.execute(query, (username, pass_hash, pass_salt))

def get_current_user(request):
    token = request.cookies.get('token', None)
    return lookup_token(token)

def user_exists(username):
    query = "SELECT user FROM users WHERE user=?"

    with sqlite3.connect('data.db') as db:
        user = db.execute(query, (username,)).fetchone()

        return bool(user)

# Token management
def generate_token(user, size=32):
    token = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(size))
    epoch_time = int(time.time())
    offset = 60 * 60 * 24; # 1 day

    query = "INSERT INTO tokens (user, token, exp) VALUES (?, ?, ?)"
    with sqlite3.connect('data.db') as db:
        user = db.execute(query, (user, token, epoch_time + offset))

    return token

def lookup_token(token):
    query = "SELECT user FROM tokens WHERE token=? AND exp>?"
    with sqlite3.connect('data.db') as db:
        user = db.execute(query, (token, int(time.time()))).fetchone()

    return user

# Password management
def verify_credentials(username, password):
    query = "SELECT password_salt FROM users WHERE user=?"
    with sqlite3.connect('data.db') as db:
        salt = db.execute(query, (username,)).fetchone()

    if salt:
        pass_hash = bcrypt.hashpw(str.encode(password), salt[0])

        query = "SELECT user FROM users WHERE user=? AND password_hash=?"
        with sqlite3.connect('data.db') as db:
            user = db.execute(query, (username, pass_hash)).fetchone()

        if user:
            return user[0]

    return None

# Chat management
def get_chats():
    query = "SELECT * FROM chats"

    with sqlite3.connect('data.db') as db:
        chats = db.execute(query).fetchmany(100)

    return chats

def create_chat(author, posted, content):
    query = "INSERT INTO chats (author, posted, content) VALUES (?, ?, ?)"

    print(author, posted, content)

    with sqlite3.connect('data.db') as db:
        db.execute(query, (author, posted, content))

# Score management
def get_scores_json():
    query = "SELECT user, bandit_score FROM users"

    with sqlite3.connect('data.db') as db:
        scores = db.execute(query).fetchall()

    return json.dumps(scores)

def update_score(user, password):
    if password == "":
        return -1

    with open('bandit_passwords.txt') as f:
        passwords = [s.strip() for s in f.readlines()]

    try:
        new_score = passwords.index(password)
    except:
        return -1

    query = "SELECT bandit_score FROM users WHERE user=?"
    with sqlite3.connect('data.db') as db:
        (score,) = db.execute(query, (user,)).fetchone()

    if new_score > score:
        query = 'UPDATE users SET bandit_score=? WHERE user=?'
        with sqlite3.connect('data.db') as db:
            scores = db.execute(query, (new_score, user))

    return new_score

@app.route("/")
def index(invalid_password=False):
    user = get_current_user(request)
    if user:
        user = user[0]
    return render_template('index.html', user=user, chats=get_chats(), invalid_password=invalid_password)

@app.route("/login", methods = ['POST'])
def login():
    user = verify_credentials(request.form['username'], request.form['password'])
    if not user:
        return index(invalid_password=True)
    else:
        resp = make_response(redirect('/'))
        resp.set_cookie('token', generate_token(user))

        return resp

@app.route("/signup", methods = ['GET', 'POST'])
def signup():
    if get_current_user(request):
        return redirect('/')

    if request.method == 'GET':
        return render_template('signup.html')

    if user_exists(request.form['username']):
        return render_template('signup.html', username_exists=request.form['username'])
    elif request.form['password'] != request.form['repassword']:
        return render_template('signup.html', different_passwords=True)
    else:
        create_user(request.form['username'], request.form['password'])
        token = generate_token(request.form['username'])

        resp = make_response(redirect('/'))
        resp.set_cookie('token', token)
        return resp

@app.route("/logout", methods = ['GET'])
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('token', 'None')

    return resp

@app.route("/update", methods = ['POST'])
def update():
    return get_scores_json();

@app.route("/score", methods = ['POST'])
def score():
    user = get_current_user(request)
    level_password = request.form['level_password']

    if not user:
        return '-1'
    else:
        user = user[0]

    score = str(update_score(user, level_password))
    return score

@socketio.on('chat')
def handle_message(data):
    try:
        token_match = lookup_token(json.loads(data['token']))
    except:
        token_match = None

    if token_match:
        user = token_match[0]
    else:
        user = 'Anonymous'

    time = datetime.now().strftime('%b %d %I:%M %p')
    msg = html.escape(data['msg'])
    create_chat(user, time, msg)
    emit('post', {'user': user, 'msg': msg, 'time': time}, json=True, broadcast=True)
    current_player = request.cookies.get('player', None)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=80)
