import streamlit as st
from tqdm import tqdm
import json
import requests  
import threading
from main import update_data

# CSS code
st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');
        body {{
            font-family: 'Roboto', sans-serif;
            animation: pulse 5s infinite;
        }}
        .output-box {{
            border: 1px solid #ddd;
            padding: 10px;
            margin-bottom: 10px;
            font-family: 'Roboto', sans-serif;
            animation: pulse 5s infinite;
        }}
        
    </style>
    """,
    unsafe_allow_html=True,
)

def update_data_with_progress(product_description, ignore_subreddits, time_cutoff_seconds, subreddits, postlimit):
    with st.empty():
        progress_bar = st.progress(0)

        # Call the update_data function and monitor progress with tqdm
        data = None  # Initialize data as None
        for progress in tqdm(update_data(product_description, ignore_subreddits, time_cutoff_seconds, subreddits, postlimit), unit="item"):
            progress_bar.progress(progress)
        
        # Store the JSON data returned by the update_data function
        data = update_data(product_description, ignore_subreddits, time_cutoff_seconds, subreddits, postlimit)

    return data  # Return the JSON data

# Title
st.title("Reddit API")

# Text box for product description
product_description = st.text_area("Product Description", key="product_desc")

# Text box for subreddit URL(s)
subreddit_urls = st.text_area("Subreddit URL(s)", key="subreddit_urls")

# Text box for subreddit(s) to ignore
ignore_subreddits = st.text_area("Subreddit(s) to Ignore", key="ignore_subreddits")

# Integer input for the number of posts to scrape per subreddit
num_posts_to_scrape = st.number_input("Number of Posts to Scrape per Subreddit", min_value=1, step=1, key="num_posts")

# Integer/Float input the epoch time, in seconds
time_cutoff_seconds = st.number_input("Epoch Time (in seconds)", min_value=0.0, key="time_cutoff_seconds")

if st.button("Update Data"):
    data = update_data_with_progress(product_description, ignore_subreddits, time_cutoff_seconds, subreddits, postlimit)

for comment_key, comment_data in data.items():
    comment_text = comment_data.get("COMMENT", "N/A")
    post = comment_data.get("POST", "N/A")
    url = comment_data.get("URL", "N/A")

    # Display values in the HTML div
    st.markdown(f"<div class='output-box'>COMMENT: {comment_text} <br>POST: {post} <br>URL: {url}</div>", unsafe_allow_html=True)
