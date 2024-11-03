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

            link_tag = item.find('a', {'class': 's-item__link'})
            link = link_tag['href'] if link_tag else 'No link found' 
            
            request = requests.get(link)
            s = BeautifulSoup(request.text, 'html.parser')
            
            attributes = []
            div_tag = s.select_one('div[data-testid="ux-layout-section-evo__item"]')
            if div_tag:
                span_tag = div_tag.find_all('span', {'class': 'ux-textspans'})
                attributes = [span.text.strip() for span in span_tag if span]
            else:
                attributes = ['No text found']
   

            # Extract the product price
            price_tag = item.find('span', {'class': 's-item__price'})
            price = price_tag.text.strip() if price_tag else 'No price found'
            
            # Append the product details to the list
            product_list.append({
                'title': title,
                'price': price,
                'link': link,
                'attributes': str(attributes).lower
            })

        return product_list

    