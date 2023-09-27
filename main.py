import os
import pandas as pd
import praw
import time
import json

# Setting up the Reddit client using PRAW
reddit = praw.Reddit(
    client_id=os.environ['CLIENT_ID'],
    client_secret=os.environ['SECRET_KEY'],
    user_agent="MyAPI/0.0.1",
    username=os.environ['ACCOUNT_USERNAME'],
    password=os.environ['ACCOUNT_PASSWORD']
)

def scrape_subreddit_hot(subreddit_url):
    subreddit_name = subreddit_url.split('/')[-2]  # Assumes the URL ends with a '/'
    subreddit = reddit.subreddit(subreddit_name)
    
    # Fetching hot posts from the specified subreddit
    hot_posts = subreddit.hot(limit=10)  # Adjust the limit as needed
    
    data_list = []
    for post in hot_posts:
        post_data = {
            "subreddit": post.subreddit.display_name,
            "title": post.title,
            "selftext": post.selftext,
            "upvote_ratio": post.upvote_ratio,
            "ups": post.ups,
            "downs": post.downs,
            "score": post.score,
            "permalink": post.permalink,
            "comments": []
        }
        
        post.comments.replace_more(limit=None)  # Fetching all comments, not just top level
        for comment in post.comments.list():
            post_data["comments"].append({
                "author": str(comment.author),
                "comment": comment.body
            })
            
        data_list.append(post_data)
        time.sleep(0.6)  # Delay to comply with rate limit
    
    df = pd.DataFrame(data_list)
    df['comments'] = df['comments'].apply(json.dumps)  # Convert comments to string representation
    
    return df

# main function calls

subreddit_url = input("Sub-Reddit URL: ")
df = scrape_subreddit_hot(subreddit_url)

filename = "reddit_data_{}.csv".format(str(time.time()))
df.to_csv(filename, index=False)

