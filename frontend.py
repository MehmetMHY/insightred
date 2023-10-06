import streamlit as st
import json
import requests  # pip install requests
from streamlit_lottie import st_lottie  # pip install streamlit-lottie
# CSS code
st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');
        body {{
            font-family: 'Roboto', sans-serif;
            animation: pulse 5s infinite;
            background-size: 100% 100%;
            background-image: url('backgroundimg.png');  # Replace with your GitHub raw image URL
            background-repeat: no-repeat;
        }}
        .custom-text-box {{
            height: 100px; /* Adjust the height as needed */
        }}
        
    </style>
    """,
    unsafe_allow_html=True,

)
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_hello = load_lottieurl("https://lottie.host/?file=e5669da7-f681-418f-b8e0-021a8e890a13/H8jy4AG3jX.json")
st_lottie(
    lottie_hello,
    speed=1,
    reverse=False,
    loop=True,
    quality="low", # medium ; high
    renderer="svg", # canvas
    height=None,
    width=None,
    key=None,
)
# Title
st.title("Reddit API")

# Text box for product description
product_paragraph = st.text_area("Product Description", key="product_desc")

# Text box for subreddit url
additional_text = st.text_area("Subreddit URL", key="subreddit_url", height=50)

# Button
if st.button("Run Code"):
    
    st.text("Fetching Comments...")

    # Simulate a job with progress
    import time
    progress_bar = st.progress(0)
    for i in range(101):
        time.sleep(0.1)
        progress_bar.progress(i)

    st.text("Results Ready!")

    # This will display any comments or outputs from your job
    st.text("Comments:")

    # Display comments here (replace with your actual comments)
    st.text("Comment 1")
    st.text("Comment 2")
