from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time

# Set up Selenium WebDriver
driver_path = "C:/Users/shaya/Desktop/Personal/justplanit/chromedriver-win64/chromedriver.exe"  # I'm using chromedriver
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# Set base url
BASE_URL = "https://www.firstplanit.com/site/productlist"

# Load the page and wait for the products to load
driver.get(BASE_URL)

try:
    # Wait until the dynamic content is fully loaded (timeout at 20 seconds)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'ProductInfo')) # Once the ProductInfo tag is located, stop waiting.
    )
except Exception as e:
    print(f"Error waiting for products to load: {e}")
    driver.quit()
    exit()

# Get the page source after JavaScript has rendered
html_content = driver.page_source
driver.quit()

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')
products = soup.find_all('div', class_='ProductInfo') # Find all ProductInfo divs

product_names = []
product_url_and_image = []

for product in products:
    product_data = {}
    try:
        h2_elements = product.find_all('h2') # the titles and types use h2 tags
        # gather both the titles and types and separate them
        name_and_type = [h2.text.strip() for h2 in h2_elements if h2]
        product_data['product_name'] = name_and_type[0]
        product_data['product_type'] = name_and_type[1]
    except AttributeError as e:
        print(f"Error extracting h2 elements from product: {e}")
    product_names.append(product_data)

products = soup.find_all('div', class_='box image') # locate images
for product in products:
    product_data = {}
    try:
        product_data['product_url'] = BASE_URL + product.find('a')['href'].strip() if product.find('a') else 'N/A'
        product_data['product_image'] = product.find('img')['src'] if product.find('img') else None
    except AttributeError as e:
        print(f"Error extracting url and image from product: {e}")
    product_url_and_image.append(product_data)


# I now have two separate data sets, unpack and combine them
product_list = list(zip(product_names, product_url_and_image))
merged_list = []
for item_pair in product_list:
    merged_item = {}
    for item in item_pair:
        merged_item = {**merged_item, **item}
    merged_list.append(merged_item)
    
# Save scraped data to a JSON file
with open('products.json', 'w', encoding='utf-8') as json_file:
    json.dump(merged_list, json_file, ensure_ascii=False, indent=4)

print(f"Scraping complete. Data saved to products.json.")
