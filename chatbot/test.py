from Resources import Resources

resource = Resources("camera")
soup = resource.get_data()
products = resource.parse(soup)
print("test")
for product in products: 
    print(product)