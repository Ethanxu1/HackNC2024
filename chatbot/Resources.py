import requests
from bs4 import BeautifulSoup
import pandas as pd

class Resources:

    def __init__(self, item):
        self.item = item
        self.url = f"https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2334524.m570.l1313&_nkw={item}&_sacat=0&_odkw=Monitors&_osacat=0"
    
    def get_data(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup

    def parse(self, soup):
        results = soup.find_all('div', {'class': 's-item__info clearfix'})
        product_list = []
        
        for item in results:
            # Extract the product title
            title_tag = item.find('span', {'role': 'heading'})
            title = title_tag.text.strip() if title_tag else 'No title found'
            
            # Extract the product price
            price_tag = item.find('span', {'class': 's-item__price'})
            price = price_tag.text.strip() if price_tag else 'No price found'
            
            # Append the product details to the list
            product_list.append({
                'title': title,
                'price': price
            })

        # Print the results
        for product in product_list:
            print(product)
