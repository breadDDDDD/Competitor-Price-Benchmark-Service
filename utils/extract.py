import time
import random
import json
import os
import hashlib
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent

# create a driver with random user agent
def get_driver(proxy=None):
    user_agent = UserAgent().random
    chrome_options = Options()
    if proxy:
        chrome_options.add_argument(f'--proxy-server=http://{proxy}')
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument(f'--window-size={random.randint(1024, 1920)},{random.randint(768, 1080)}')
    return webdriver.Chrome(options=chrome_options)

# hash function
def get_hash(item):
    """Generate a unique hash for each product based on key fields."""
    string = f"{item['title']}_{item['price']}_{item['rating']}"
    return hashlib.sha256(string.encode()).hexdigest()

# extract data from the website
def extract_books(driver, url):
    """Scrape books from the website, handling pagination."""
    driver.get(url)
    books_data = []

    while True:
        books = driver.find_elements(By.CSS_SELECTOR, "article.product_pod")
        for book in books:
            title_element = book.find_element(By.CSS_SELECTOR, "h3 a")
            title = title_element.get_attribute("title")
            price = book.find_element(By.CSS_SELECTOR, ".price_color").text
            relative_url = title_element.get_attribute("href")
            rating = book.find_element(By.CSS_SELECTOR, "p.star-rating").get_attribute("class").split()[-1]

            books_data.append({
                "title": title,
                "price": price,
                "rating": rating,
                "url": relative_url
            })

        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "li.next a")
            next_url = next_btn.get_attribute("href")
            driver.get(next_url)
            time.sleep(1)
        except:
            break

    return books_data

# to extract new products only
def extract_new_products(raw_products, hash_file, books_file):
    """Filter out previously processed products using hash-based deduplication."""
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            seen_hashes = set(json.load(f))
    else:
        seen_hashes = set()

    new_products = []
    new_hashes = []

    for item in raw_products:
        item_hash = get_hash(item)
        if item_hash not in seen_hashes:
            new_products.append(item)
            new_hashes.append(item_hash)

    # Save updated hashes
    all_hashes = list(seen_hashes.union(new_hashes))
    with open(hash_file, "w") as f:
        json.dump(all_hashes, f)
        
    if os.path.exists(books_file):
        with open(books_file, "r", encoding="utf-8") as f:
            all_books = json.load(f)
    else:
        all_books = []

    # Append new books and save back
    all_books.extend(new_products)
    with open(books_file, "w", encoding="utf-8") as f:
        json.dump(all_books, f, indent=2, ensure_ascii=False)

    return new_products

# to extract the summary of the book
def extract_summary(url, proxy=None):
    driver = get_driver(proxy)
    try:
        driver.get(url)
        time.sleep(2)
        description_header = driver.find_element(By.ID, "product_description")
        description = description_header.find_element(By.XPATH, "following-sibling::p").text
        return description
    except Exception as e:
        print("Error extracting description:", e)
        return "No description available."
    finally:
        driver.quit()

# to identify the tag of the book
def classify_tag(input_summary):
    # load the token and model URL from .env
    with open(".env/TOKENS.txt", "r") as f:
        hf_token = f.read().strip()
        os.environ["HF_TOKEN"] = hf_token
    with open(".env/model.txt", "r") as f:
        model_url = f.read().strip()
        
    if not hf_token:
        raise ValueError("HF token is empty!")

    if not model_url:
        raise ValueError("Model URL is empty!")

    # inference API 
    API_URL = model_url
    headers = {
        "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
    }

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    output = query({
        "inputs": input_summary,
        "parameters": {"candidate_labels": ["Best Seller", "Niche", "General", "Academic", "Indie"]},
    })
    highest = output["labels"][0]
    return highest


