import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_pymongo import PyMongo
import re
import jwt
from functools import wraps
import os
from dotenv import load_dotenv
import re
import threading
import HunterV1.Main
import string
import random
from datetime import timedelta

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

def GenRandomID(length=16):
    characters = string.ascii_letters + string.digits
    random_id = ''.join(random.choices(characters, k=length))
    return random_id

@app.route('/')
@login_required
def home():
    # return f"Hello, {session['name']}, {session["email"]}! <br><a href='/logout'>Logout</a>"
    return f"Hello, {session['name']}, {session['email']}! <br><a href='/logout'>Logout</a>"

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

@app.route("/search", methods=["GET"])
@login_required
def search():
    return render_template("search.html")

@app.route("/report", methods=["POST"])
@login_required
def report():
    url = request.form.get("search", "")
    
    domain = re.sub(r'^https?://', '', url)
    domain = re.sub(r'^www\.', '', domain)
    url = domain.split('/')[0]
    
    document = mongo.db.reports.find({"url": url}).sort("timestamp", -1).limit(1)

    if len(list(document)) > 0:
        document = mongo.db.reports.find({"url": url}).sort("timestamp", -1).limit(1)
        first_doc = next(document, None)
        if first_doc:
            doc_timestamp = first_doc.get("timestamp")
            doc_time = datetime.datetime.fromisoformat(doc_timestamp)
            current_time = datetime.datetime.now()
            if current_time - doc_time <= timedelta(days=7):
                dss = {
                    "summary": first_doc["siteanalysis"]["summary"]
                }
                return redirect(url_for("result", report_id=first_doc["id"]))

    randomid = GenRandomID()
    timestamp = datetime.datetime.now().isoformat()

    ds = {
        "id": randomid,
        "timestamp": timestamp,
        "url": url,
        "status": "inprogress",
        "user": session['email']
    }

    mongo.db.reports.insert_one(ds)

    thread = threading.Thread(target=HunterV1.Main.Main, args=(url, randomid, timestamp, mongo, ))
    thread.daemon = True
    thread.start()

    return render_template("loading.html", report_id=randomid, timestamp=timestamp)

@app.route("/status/<report_id>")
@login_required
def status(report_id):
    record = mongo.db.reports.find_one({"id": report_id})
    if record:
        return {"status": record.get("status", "unknown")}
    return {"status": "not_found"}

@app.route("/result/<report_id>")
@login_required
def result(report_id):
    record = mongo.db.reports.find_one({"id": report_id})
    if record and record.get("status") == "completed":
        return render_template("report.html", id=report_id, data=record) 
    return "Report not found or not ready yet."

@app.route("/whois/<report_id>")
@login_required
def WhoisData(report_id):
    record = mongo.db.reports.find_one({"id": report_id})
    if record and record.get("status") == "completed":
        return render_template("whois.html", id=report_id, data=record["whois"]) 
    return "Report not found or not ready yet."

@app.route("/ip/<report_id>")
@login_required
def IPData(report_id):
    record = mongo.db.reports.find_one({"id": report_id})
    if record and record.get("status") == "completed":
        return render_template("ipdata.html", id=report_id, data=record["ipdata"]) 
    return "Report not found or not ready yet."

def transform_dns_records(data):
    if data is None:
        return {} 
    
    transformed = {}
    
    if 'A' in data and data['A']:
        transformed['A'] = [{'Content': record['Content'], 'TTL': record['TTL']} for record in data['A']]
    
    if 'AAAA' in data and data['AAAA']:
        transformed['AAAA'] = [{'Content': record['Content'], 'TTL': record['TTL']} for record in data['AAAA']]
    
    if 'MX' in data and data['MX']:
        transformed['MX'] = [{'Content': record['Exchange'], 'Preference': record['Preference'], 'Exchange': record['Exchange'], 'TTL': record['TTL']} for record in data['MX']]
    
    if 'NS' in data and data['NS']:
        transformed['NS'] = [{'Content': record['Content'], 'TTL': record['TTL']} for record in data['NS']]
    
    if 'TXT' in data and data['TXT']:
        transformed['TXT'] = [{'Content': record['Content'], 'TTL': record['TTL']} for record in data['TXT']]
    
    if 'SOA' in data and data['SOA']:
        transformed['SOA'] = [{'Mname': record['Mname'], 'Rname': record['Rname'], 'Serial': record['Serial'], 
                               'Refresh': record['Refresh'], 'Retry': record['Retry'], 
                               'Expire': record['Expire'], 'Minimum': record['Minimum'], 
                               'TTL': record['TTL']} for record in data['SOA']]
    
    if 'PTR' in data and data['PTR']:
        transformed['PTR'] = [{'Content': record['Content']} for record in data['PTR']]
    
    return transformed

@app.route("/dns/<report_id>")
@login_required
def dns(report_id):
    record = mongo.db.reports.find_one({"id": report_id})
    if record and record.get("status") == "completed":
        transformed_data = transform_dns_records(record['dnsrecords'])
        return render_template("dns.html", id=report_id, data=transformed_data) 
    return "Report not found or not ready yet."

@app.route("/siteanalysis/<report_id>")
@login_required
def siteanalysis(report_id):
    record = mongo.db.reports.find_one({"id": report_id})
    if record and record.get("status") == "completed":
        return render_template("siteanalysis.html", id=report_id, data=record["siteanalysis"]) 
    return "Report not found or not ready yet."

@app.route("/mailserver/<report_id>")
@login_required
def mailserver(report_id):
    record = mongo.db.reports.find_one({"id": report_id})
    if record and record.get("status") == "completed":
        return render_template("mailservers.html", id=report_id, data=record["mailservers"]) 
    return "Report not found or not ready yet."

@app.route("/metadata/<report_id>")
@login_required
def metadata(report_id):
    record = mongo.db.reports.find_one({"id": report_id})
    if record and record.get("status") == "completed":
        return render_template("metadata.html", id=report_id, data=record["metadata"]) 
    return "Report not found or not ready yet."

@app.route("/headers/<report_id>")
@login_required
def headers(report_id):
    record = mongo.db.reports.find_one({"id": report_id})
    if record and record.get("status") == "completed":
        return render_template("headers.html", id=report_id, data=record["headers"]) 
    return "Report not found or not ready yet."

@app.route("/ssl/<report_id>")
@login_required
def ssl(report_id):
    record = mongo.db.reports.find_one({"id": report_id})
    if record and record.get("status") == "completed":
        return render_template("ssl.html", id=report_id, data=record["ssl"]) 
    return "Report not found or not ready yet."

@app.route("/openports/<report_id>")
@login_required
def openports(report_id):
    record = mongo.db.reports.find_one({"id": report_id})
    if record and record.get("status") == "completed":
        return render_template("openports.html", id=report_id, data=record["openports"]) 
    return "Report not found or not ready yet."

@app.route("/history")
@login_required
def history():
    history = mongo.db.reports.find({"user": session['email']})
    return f"{len(list(history))}"

@app.template_filter('get_last_part')
def get_last_part(url):
    return url.split('/')[-1]

@app.template_filter('capitalize_first')
def capitalize_first(text):
    return text.split('.')[0].capitalize()

app.jinja_env.filters['get_last_part'] = get_last_part
app.jinja_env.filters['capitalize_first'] = capitalize_first

if __name__ == '__main__':
    app.run(debug=True, port=5000)