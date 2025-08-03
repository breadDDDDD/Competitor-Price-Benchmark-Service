from utils.extract import get_driver, extract_books,extract_new_products, get_hash
from utils.transform import transform_books
from utils.load import save_to_json, print_json, append_to_json
import json

# define the files and link
url = "https://books.toscrape.com/"
hash_file = 'processed_hashes.json'
file_name = "books.json"

def main(proxy=None):
    driver = get_driver(proxy)
    try:
        # extract book data
        raw_books = extract_books(driver, url)
        new_data = extract_new_products(raw_books, hash_file, file_name)
        if new_data == []:
        #   for no new products/first run
            print("No new products found.")
                
            ''' commented unless need to run for the first time'''
            # clean_books = transform_books(raw_books)
            # save_to_json(clean_books, file_name)
            # hashes = [get_hash(book) for book in clean_books]
            # save_to_json(hashes, hash_file)
        else:   
        # new products only
            clean_new = transform_books(new_data)
            append_to_json(clean_new, file_name)
            
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
