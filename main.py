from flask import Flask, render_template, request, jsonify, make_response, g
from markupsafe import escape
from flask_wtf.csrf import CSRFProtect
import json
import os
import bcrypt
import speech_recognition as sr
import pyttsx3
import cv2
import pytesseract
import openai
from datetime import date
from supabase import create_client, Client

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
csrf = CSRFProtect(app)
openai.api_key = os.getenv("OPENAI_API_KEY", "your_default_key_here")
engine = pyttsx3.init()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_db():
    if 'db' not in g:
        g.db = supabase
    return g.db

@app.teardown_appcontext
def close_db(exception):
    pass

@app.route("/")
def home():
    usrnm = request.cookies.get("userLogin")
    data = {"username": str(usrnm)}
    return render_template('index.html', data=data)

@app.route("/loginAndSignup")
def loginAndSignup():
    return render_template('loginAndSignup.html')

@app.route('/process_string', methods=['POST'])
@csrf.exempt 
def process_string():
    print("checkpoint 0")
    input_string = request.form.get('input_string', '')
    user_login_cookie = request.cookies.get('userLogin')
    if not user_login_cookie:
        return jsonify(result="Please login before using the AI.")
    sanitized_string = escape(input_string)

    print("checkpoint 2")

    if not sanitized_string:
        return jsonify({"error": "No question provided"}), 400
    
    print("checkpoint 2")

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": sanitized_string}]
    )
    answer = response.choices[0].message.content

    print(answer)

    return jsonify(result=answer)

@app.route('/addUser', methods=['POST'])
@csrf.exempt 
def addUser():
    data = request.get_json()
    userData = data['input_json']
    username = userData['username']
    password = userData['password']
    email = str(userData['email'])
    signupDate = date.today().strftime("%Y-%m-%d")

    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt)

    db = get_db()

    # Check if username exists
    result = db.table('loginInfo').select('username').eq('username', username).execute()
    if result.data:
        return "Sorry this username is already in use."

    # Add new user
    new_user = {
        'username': username,
        'password': hashed_password.decode('utf-8'),
        'email': email,
        'banned': False,
        'signupDate': signupDate,
        'banDate': None
    }
    db.table('loginInfo').insert(new_user).execute()

    return "New user created."

@app.route('/validateLogin', methods=['POST'])
@csrf.exempt 
def validateLogin():
    data = request.get_json()
    userData = data['input_json']
    username = userData['username']
    password = userData['password']

    db = get_db()

    result = db.table('loginInfo').select('password').eq('username', username).execute()
    if result.data:
        stored_hashed_password = result.data[0]['password']
        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
            response = make_response("Login successful.")
            response.set_cookie(
                key='userLogin', 
                value=username, 
                httponly=True,
                secure=True,
                samesite='Strict',
                max_age=3600
            )
            return response

    return "Invalid username or password."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
