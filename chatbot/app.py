from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import requests
import logging
from flask_sqlalchemy import SQLAlchemy
from LoanCalculator import StudentInterestCalculator
from Search import Search
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

api_key = os.getenv('OPENAI_KEY')


# Define detailed prompts for assisting a wealth manager with clients
prompts = {
    "financial calculator": "Hi there! I'm FINram (FINny), here to help with your financial planning needs as a student. How can I help you navigate the calculator today? Feel free to ask about any of the features. I hope that this calculator is helpful!",
    "Help with errors": "Let me see what's going on here. It seems that you may have selected a repayment plan that is too short to pay off your loan with the current specified disposable income. Try changing the length of your plan or the available disposable income.",
    "principal": "The principal is the amount of debt you currently have.",
    "rate": "If you know what your interest rate is, you should input it under the rate column. Otherwise, I have a default rate of 5.00 percent set up for use!",
    "time": "Here is what you can do with the time feature. I put in a default value of repayment of loan within one year, but you can change the values in this column to create repayment plans of different lengths (and find their respective monthly payments!)",
    "other": "I'm happy to help you with more financial questions you may have as a UNC student. However, I am still learning about such topics and would suggest you refer to the UNC Scholarships and Student Aid page first.",
    "Budget Planner": "Let's map out your budget! Tell me your monthly income, fixed expenses (like rent or tuition), and flexible expenses (like groceries or entertainment), and I’ll help you see where you might save or adjust. Let's work toward a balanced budget!",
    "authors": "I, FINny, am the result of the efforts of Akshara, Ethan, Mihika, and Shourish. They hope you found this site (prototype) helpful!",
    "Emergency Fund Calculator" : "Do you have an emergency fund goal? An emergency fund is there for unexpected expenses, like car repairs or medical bills. Let's calculate how much you might need based on your expenses and lifestyle!",
    "Scholarship and Grant Finder" : "Did you know there are tons of scholarships and grants available? I can guide you on where to search, from local scholarships to more national opportunities. Saving on tuition costs is a win!",
    "Tax Tips" :  "Filing taxes for the first time? I can provide tips on student tax deductions, including credits for tuition, textbooks, and other college-related expenses.",
    "Financial Wellness Tips" : "Want to build healthy financial habits? I can share quick tips and reminders, like setting small goals, managing impulse spending, and reviewing your budget monthly."

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

@app.route('/search.html', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        print("method ran")
        
        print("Starting scrape")
        data = request.json
        item = data['item']
        features = data['features']

        resource = Search(item)
        soup = resource.get_data()
        products = resource.parse(soup)
        selectedProducts = []
        
        print("Parsing array ...")
        for product in products:
            for feature in features:
                if feature.lower() in product['attributes']:
                    selectedProducts.append(product)
                    break
        print("finished parsing file")
        # Sort selected products by price and get the top 5 lowest cost items
        top_5_products = sorted(selectedProducts, key=lambda x: x['price'])[:5]

        # Prepare the results to be rendered in the HTML div with id "output"
        output_html = ""
        for product in top_5_products:
            output_html += f"<div><h3>{product['title']}</h3><p>Price: ${product['price']}</p><a href='{product['link']}'>View Product</a></div>"
        print(output_html)
        return render_template('/search.html', output=output_html)


    else:
        print("error, method not post")

    return render_template('search.html')

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
        return jsonify({'response': 'Please provide a scenario.'}), 400

    # Check if the scenario is valid and get the prompt
    prompt = prompts.get(scenario)
    if not prompt:
        return jsonify({'response': 'Enter a valid prompt.'}), 400

    # If the scenario has changed, reset conversation and return only the prompt
    if session.get('chat_state') != scenario:
        session['chat_state'] = scenario
        session['conversation'] = []  # Reset the conversation when the scenario changes
        return jsonify({'response': prompt})

    # Get user input and generate response using OpenAI API
    user_input = message
    response = get_openai_response(user_input, scenario)

    return jsonify({'response': response})

@app.route('/resources')
def resources():
    return render_template('resources.html')



if __name__ == "__main__":
    app.run(debug=True)