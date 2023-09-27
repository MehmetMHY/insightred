import os
import pandas as pd
import praw

# Setting up the Reddit client using PRAW
reddit = praw.Reddit(
    client_id=os.environ['CLIENT_ID'],
    client_secret=os.environ['SECRET_KEY'],
    user_agent="MyAPI/0.0.1",
    username=os.environ['ACCOUNT_USERNAME'],
    password=os.environ['ACCOUNT_PASSWORD']
)

# Fetching new posts from the 'python' subreddit
new_posts = reddit.subreddit('python').hot(limit=100)

data_list = []
for post in new_posts:
    data_list.append({
        "subreddit": post.subreddit.display_name,
        "title": post.title,
        "selftext": post.selftext,
        "upvote_ratio": post.upvote_ratio,
        "ups": post.ups,
        "downs": post.downs,
        "score": post.score,
        "permalink": post.permalink
    })

df = pd.DataFrame(data_list)

# Make sure data_list has been populated
print(f'Number of posts fetched: {len(data_list)}')

# Fetching and printing all comments for the first post
first_post = reddit.submission(url=f"https://www.reddit.com{data_list[0]['permalink']}")
first_post.comments.replace_more(limit=None)  # Fetching all comments, not just top level
comments_list = first_post.comments.list()

# Check the number of comments fetched
print(f'Number of comments fetched: {len(comments_list)}')

for comment in comments_list:
    print(f"Author: {comment.author}")
    print(f"Comment: {comment.body}")
    print('---')

