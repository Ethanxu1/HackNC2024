from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import requests
import logging
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json
from LoanCalculator.py import StudentInterestCalculator 

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Your OpenAI API key
api_key = "sk-proj-7bLYALOdq524pvA9UQ4sT3BlbkFJoGws4ktP1CQljV0d0OQ5"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define detailed prompts for assisting a wealth manager with clients
prompts = {
    "initial_consultation": "Hi there! I'm here to help with your client's financial planning needs. What are you looking for assistance with today? We can explore investment options, retirement strategies, or ways to optimize their taxes. Feel free to share any initial thoughts or questions you have.",
    "financial_goal_setting": "Let's chat about your client's financial goals. Are they saving for something specific like a new home, education, or retirement? Or perhaps they have other short-term or long-term targets in mind? Share any details you have, and we can start planning.",
    "tax_optimization": "Would you like to look into tax-saving opportunities for your client? We can review their current tax situation and explore ways to improve it. You can tell me a bit about their income, tax bracket, or any tax strategies they’re currently using or interested in.",
    "retirement_planning": "Let's talk about your client's retirement plans. Do they have a target retirement age or a vision for their retirement lifestyle? We can work on how much they need to save and discuss their current savings and plans. Share what you can, and we'll go from there.",
    "estate_planning": "Does your client have any estate planning needs? We can review and update their plans to ensure they align with their wishes. Tell me about their assets, beneficiaries, or any specific changes they want to make. Do they have any wills, trusts, or other documents?",
    "investment_recommendations": "I can help with personalized investment recommendations for your client. What is their comfort level with risk and how long do they plan to invest? Are there specific funds or asset classes they’re interested in, or particular performance metrics they focus on?",
    "budgeting": "Are you working on creating a budget for your client? Let's start by discussing their income and monthly expenses. We can then set financial goals and create a plan to manage their spending. Share any details you have about their financial situation.",
    "debt_management": "Is your client looking for ways to manage and reduce their debt? We can talk about their current debts and develop a strategy to pay them off efficiently. Let me know about the types of debt, amounts, interest rates, and any repayment plans they have.",
    "other": "I'm here to assist you with any other financial inquiries. Please provide details about what your client needs help with."
}

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Conversation model
class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scenario = db.Column(db.String(80), nullable=False)
    messages = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('conversations', lazy=True))

# Create the database tables within the application context
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            return "Username already taken. Please choose a different one."

        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        conversations = Conversation.query.filter_by(user_id=user.id).all()
        return render_template('dashboard.html', username=session['username'], conversations=conversations)
    return redirect(url_for('login'))

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    principal = float(data['principal'])
    disposable_income = float(data['disposableIncome'])
    rate = float(data.get('rate', 5.0))
    time = float(data.get('time', 1))

    calculator = StudentInterestCalculator(principal, disposable_income, rate, time)


def get_openai_response(user_input, scenario):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': 'You are a helpful financial assistant.'},
            {'role': 'user', 'content': prompts.get(scenario, "How can I assist you with your financial needs today?")},
            {'role': 'user', 'content': user_input}
        ]
    }
    try:
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        return response_json['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return "An error occurred while processing your request. Please try again later."

@app.route('/chat', methods=['POST'])
def chat():
    if 'username' not in session:
        return jsonify({'response': 'Please log in to use the chat feature.'}), 403

    data = request.json
    scenario = data.get('scenario')
    message = data.get('message')

    if not scenario:
        return jsonify({'response': 'No scenario provided.'}), 400

    # Check if the scenario has changed
    if session.get('chat_state') != scenario:
        session['chat_state'] = scenario
        session['conversation'] = []  # Reset the conversation when the scenario changes
        return jsonify({'response': prompts.get(scenario, 'No prompt found for this scenario.')})

    user_input = message
    response = get_openai_response(user_input, scenario)

    # Save the conversation to the session
    if 'conversation' not in session:
        session['conversation'] = []
    
    session['conversation'].append({'role': 'user', 'content': user_input})
    session['conversation'].append({'role': 'assistant', 'content': response})

    # Save the conversation to the database
    user = User.query.filter_by(username=session['username']).first()
    if data.get('end_scenario'):
        conversation = Conversation(
            user_id=user.id,
            scenario=scenario,
            messages=json.dumps(session['conversation'])
        )
        db.session.add(conversation)
        db.session.commit()
        session.pop('conversation', None)
        session.pop('chat_state', None)

    return jsonify({'response': response})

if __name__ == "__main__":
    app.run(debug=True)