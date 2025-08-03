import json
import os
import hashlib

# save the file into json format
def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# add new data to existing json file without duplicates
def append_to_json(new_data, filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    seen = set()
    combined_data = []
    
    def get_hash(item):
        string = f"{item['title']}_{item['price']}_{item['rating']}"
        return hashlib.sha256(string.encode()).hexdigest()

    for item in existing_data + new_data:
        item_hash = get_hash(item)
        if item_hash not in seen:
            seen.add(item_hash)
            combined_data.append(item)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
 
# to print json data in a readable format
def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


