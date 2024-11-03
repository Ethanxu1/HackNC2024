# HackNC2024
Project idea: A UNC Student’s guide to finance 

**Main webpage:**

- [ ]  Student loan interest calculator (SLIC)
- [ ]  Student Help Chatbot (chatbot)
- [ ]  FAFSA information (fafsa)
- [ ]  Scholarship recommendations (scholarship)
- [ ]  Investment Recommendations (invenstment)
- [ ]  Student discounts (discounts)
- [ ]  Budgeting/ Financial goal setting (budgeting)

How to run the code:
run app.py 

dependancies:
flask
requests
logging
flask_sqlalchemy
bs4
Our Usage:

First, we used financial formulas we found online (such as compound interest calculation) in our calculator functions. Our calculator was the main feature, and we improved the formatting of the website (using our code for the front end) by asking ChatGPT how to format the text boxes to look a specific way. For our chatbot, it puts calls through to the ChatGPT API to inform users on how to navigate the calculator we built, along with providing further resources if they are interested. We had 2 secondary features that linked to resources and a search feature for discounted items (we web scraped eBay). We also put in our front end code for the search function to ChatGPT to format it further, but we created most of the code for the front-end overall. We used the FLASK framework in Python.

One issue that came up was that our back-end for the search function was not rendering on the web page even though the web scraping code was working. Our time was limited, otherwise we would have addressed this issue. To create a working demo, we input some sample data to display on that page. We also added some print functions to the back-end code for the search feature so that the output of the code could be displayed if ran in an IDE.
