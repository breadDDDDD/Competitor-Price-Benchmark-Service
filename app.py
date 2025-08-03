import streamlit as st
import json
import pandas as pd
from utils.match import match_product
from utils.extract import extract_summary, classify_tag

# load and prepare dataset
with open("books.json", "r", encoding="utf-8") as f:
    all_books = json.load(f)
books_df = pd.DataFrame(all_books)

st.set_page_config(layout="wide")
st.markdown(
    """
    <div style="
        background-color: #79BFA1;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 20px;
    ">
        <h1 style="color: white; margin: 0;">Competitor Benchmark Tool</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# create two columns layout
left_col, right_col = st.columns([2, 3])

# full dataset
with left_col:  
    st.header(" All Titles")
    book_table = st.dataframe(
        books_df,
        use_container_width=True,
        height=550
    )

# the comparison and summary section
with right_col:
    st.header("Title Comparison and Summary")
    
    col1, col2 = st.columns(2)
    with col1:
        my_title = st.text_input("Your Book Title")
    with col2:
        comp_title = st.text_input("Competitor Book Title")
    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:
        compare_clicked = st.button("Compare")

    with btn_col2:
        summary_clicked = st.button("Show Competitor Summary")


    # compare
    if compare_clicked:
        if not my_title or not comp_title:
            st.warning("Please enter both book titles.")
        else:
            my_product = next(
                (b for b in all_books if b["title"].strip().lower() == my_title.strip().lower()), None
            )
            comp_product = next(
                (b for b in all_books if b["title"].strip().lower() == comp_title.strip().lower()), None
            )

            if my_product and comp_product:
                score = match_product(my_product, [comp_product])
                diff = my_product["price"] - comp_product["price"]
                pct = diff / comp_product["price"] * 100

                result_df = pd.DataFrame({
                    "Your Title": [my_product["title"]],
                    "Your Price": [my_product["price"]],
                    "Your Rating": [my_product["rating"]],
                    "Competitor Title": [comp_product["title"]],
                    "Competitor Price": [comp_product["price"]],
                    "Competitor Rating": [comp_product["rating"]],
                    "Rating Difference": [my_product["rating"] - comp_product["rating"]],
                    "Price Difference": [f"{diff:.2f} ({pct:.2f}%)"],
                    "Match Score (%)": [score]
                })

                st.success("✅ Match Result")
                st.table(result_df)
            else:
                if not my_product:
                    st.error(f" Your book '{my_title}' was not found in the dataset.")
                if not comp_product:
                    st.error(f" Competitor book '{comp_title}' was not found in the dataset.")

    # summary
    if summary_clicked:
        comp_product = next(
            (b for b in all_books if b["title"].strip().lower() == comp_title.strip().lower()), None
        )
        if comp_product:
            comp_url = comp_product.get("url")
            if comp_url:
                with st.spinner("Extracting summary..."):
                    summary = extract_summary(comp_url, proxy=None)
                    tag = classify_tag(summary)
                st.subheader("Competitor Book Summary")
                st.write(summary)
                st.markdown(
                    f"""
                    <div style="
                        background-color:#330000;
                        border: 2px solid #990000;
                        color:#ffcccc;
                        padding: 10px;
                        border-radius: 8px;
                        display: inline-block;
                        margin-top: 5px;
                    ">
                        <strong>Tag:</strong> {tag}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.warning("No URL found for competitor product.")
        else:
            st.warning("Competitor product not found.")
