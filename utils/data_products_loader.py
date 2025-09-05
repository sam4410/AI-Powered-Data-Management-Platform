import json

def load_data_products_config():
    with open("ecommerce_data_products.json", "r") as f:
        return json.load(f)
