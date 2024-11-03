from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import requests
import logging
from flask_sqlalchemy import SQLAlchemy
from LoanCalculator import StudentInterestCalculator

 

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Your OpenAI API key
api_key = "sk-proj-7bLYALOdq524pvA9UQ4sT3BlbkFJoGws4ktP1CQljV0d0OQ5"


# Define detailed prompts for assisting a wealth manager with clients
prompts = {
    "financial calculator": "Hi there! I'm FINram (FINny), here to help with your financial planning needs as a student. How can I help you navigate the calculator today? Feel free to ask about any of the features. I hope that this calculator is helpful!",
    "disposable income": "Let's talk about your disposable income. The calculator is asking for how much total money you are willing to allot to student loan repayments annually. I would suggest putting different amounts to test different plans until you find your optimal one. Not all repayment plans work with all amounts of disposable income.",
    "error": "Let me see what's going on here. It seems that you may have selected a repayment plan that is too short to pay off your loan with the current specified disposable income. Try changing the length of your plan or the available disposable income.",
    "principal": "The principal is the amount of debt you currently have.",
    "rate": "If you know what your interest rate is, you should input it under the rate column. Otherwise, I have a default rate of 5.00 percent set up for use!",
    "time": "Here is what you can do with the time feature. I put in a default value of repayment of loan within one year, but you can change the values in this column to create repayment plans of different lengths (and find their respective monthly payments!)",
    "other": "I'm happy to help you with more financial questions you may have as a UNC student. However, I am still learning about such topics and would suggest you refer to the UNC Scholarships and Student Aid page first.",
    "FINny": "Hey there, what can I help you with?",
    "authors": "I, FINny, am the result of the efforts of Akshara, Ethan, Mihika, and Shourish. They hope you found this site (prototype) helpful!"
}

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
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html') 

@app.route('/student-calculator.html', methods=['GET', 'POST'])
def student_calculator():
    if request.method == 'POST':
        data = request.json
        principal = float(data['principal'])
        disposable_income = float(data['disposable_income'])
        rate = float(data.get('rate', 5.0))
        time = float(data.get('time', 1))
        
        # Create an instance of the calculator
        calculator = StudentInterestCalculator(principal, disposable_income, rate, time)
        
        try:
            monthly_payment = calculator.calculate_monthly_payment(int(data.get('number_of_months', 12)))
            total_amount = calculator.calculate_total_amount()
            
            return jsonify({
                "monthly_payment": monthly_payment,
                "total_amount": total_amount
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    return render_template('student-calculator.html')



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
    data = request.json
    scenario = data.get('scenario')
    message = data.get('message')

    if not scenario:
        return jsonify({'response': 'No scenario provided.'}), 400

    # Check if the scenario has changed
    if session.get('chat_state') != scenario:
        session['chat_state'] = scenario
        session['conversation'] = []  # Reset the conversation when the scenario changes
        return jsonify({'response': prompts.get(scenario, 'Enter a valid prompt.')})

    user_input = message
    response = get_openai_response(user_input, scenario)

    return jsonify({'response': response})

if __name__ == "__main__":
    app.run(debug=True)
