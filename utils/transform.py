# changes the data format of ratings into int
def rating_to_int(rating_str):
    mapping = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    return mapping.get(rating_str, 0)

# changes the data format of prices into float and remove the pound sign
def clean_price(price_str):
    return float(price_str.replace("£", "").strip())

def transform_books(raw_books):
    for book in raw_books:
        book["rating"] = rating_to_int(book["rating"])
        book["price"] = clean_price(book["price"])
    return raw_books