import os
import pandas as pd
import praw
import time
import json

reddit = praw.Reddit(
    client_id=os.environ['CLIENT_ID'],
    client_secret=os.environ['SECRET_KEY'],
    user_agent="MyAPI/0.0.1",
    username=os.environ['ACCOUNT_USERNAME'],
    password=os.environ['ACCOUNT_PASSWORD']
)

def scrape_subreddit_hot(subreddit_url):
    subreddit_name = subreddit_url.split('/')[-2]
    subreddit = reddit.subreddit(subreddit_name)
    
    hot_posts = subreddit.hot(limit=10)
    
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
        
        post.comments.replace_more(limit=None)
        for comment in post.comments.list():
            post_data["comments"].append({
                "author": str(comment.author),
                "comment": comment.body
            })
            
        data_list.append(post_data)
        time.sleep(0.6)
    
    df = pd.DataFrame(data_list)
    df['comments'] = df['comments'].apply(json.dumps)
    
    return df

# main function calls

subreddit_url = input("Sub-Reddit URL: ")
df = scrape_subreddit_hot(subreddit_url)

filename = "reddit_data_{}.csv".format(str(time.time()))
df.to_csv(filename, index=False)

