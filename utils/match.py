from rapidfuzz import fuzz
import os
import requests

# Match products based on title, rating, and price
def match_product(my_product, competitor_products, title_weight=0.6, rating_weight=0.2, price_weight=0.2):

    for comp in competitor_products:
        title_score = fuzz.token_sort_ratio(my_product["title"], comp["title"]) / 100
        rating_diff = abs(my_product["rating"] - comp["rating"])
        rating_score = max(0, 1 - (rating_diff / 5))
        price_diff_pct = abs(my_product["price"] - comp["price"]) / max(comp["price"], 1e-3)
        price_score = max(0, 1 - price_diff_pct)

        combined_score = (
            title_weight * title_score +
            rating_weight * rating_score +
            price_weight * price_score
        )

    return round(combined_score * 100, 2)