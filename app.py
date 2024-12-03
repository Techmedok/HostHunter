import requests
import pytz
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_pymongo import PyMongo
import re
import jwt
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('AppSecret')

JWT_SECRET_KEY = os.getenv('JWTSecret')  
JWT_ALGORITHM = 'HS256'  

app.config["MONGO_URI"] = os.getenv('MongoCreds')  
mongo = PyMongo(app)

def create_jwt_token(email, name):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
    payload = {
        'email': email,
        'name': name,
        'exp': expiration_time
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  
    except jwt.InvalidTokenError:
        return None  

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get('jwt_token')
        if not token:
            flash('You need to log in first!', 'error')
            return redirect(url_for('login'))
        
        user_data = verify_jwt_token(token)
        if not user_data:
            session.pop('jwt_token', None)  
            flash('Your session has expired. Please log in again.', 'error')
            return redirect(url_for('login'))
        
        session['email'] = user_data['email']
        session['name'] = user_data['name']
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def home():
    return f"Hello, {session['name']}! <br><a href='/logout'>Logout</a>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = mongo.db.users.find_one({'email': email})
        
        if user:
            stored_password_hash = user['password']
            if check_password_hash(stored_password_hash, password):
                token = create_jwt_token(email, user['name'])
                session['jwt_token'] = token
                session['email'] = email
                session['name'] = user['name']
                return redirect(url_for('home'))
            else:
                flash('Invalid password!', 'error')
        else:
            flash('Email does not exist!', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email format!', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        password_hash = generate_password_hash(password)
        
        if mongo.db.users.find_one({'email': email}):
            flash('Email already exists!', 'error')
        else:
            mongo.db.users.insert_one({'name': name, 'email': email, 'password': password_hash})
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('name', None)
    session.pop('jwt_token', None)  
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/whois', methods=['GET', 'POST'])
def route():
    if request.method == 'POST':
        url = request.form.get('url')
        requesturl = "https://who-dat.as93.net/" + url
        response = requests.get(requesturl)
        data = response.json()

        domainname = data["domain"]["domain"]
        registrar = data["registrar"]["name"]
        regdate = data["domain"]["created_date"]
        expdate = data["domain"]["expiration_date"]
        rendate = data["domain"]["expiration_date_in_time"]

        regdate = datetime.datetime.strptime(regdate, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)

        return render_template('whois1.html', domain = domainname, registrar=registrar, regdate=regdate, expdate=expdate, rendate=rendate)
    return render_template('whois.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)