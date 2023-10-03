import os
import pandas as pd
import praw
import time
import json
import datetime

reddit = praw.Reddit(
    client_id=os.environ['CLIENT_ID'],
    client_secret=os.environ['SECRET_KEY'],
    user_agent="MyAPI/0.0.1",
    username=os.environ['ACCOUNT_USERNAME'],
    password=os.environ['ACCOUNT_PASSWORD']
)


def scrape_subreddit_hot(subreddit_url, limit=10):
    subreddit_name = subreddit_url.split('/')[-2]
    subreddit = reddit.subreddit(subreddit_name)

    hot_posts = subreddit.hot(limit=limit)

    data_list = []
    for post_index, post in enumerate(hot_posts, start=1):
        if post.stickied:  # Skip if the post is pinned
            print(f"---> Skipping pinned post {post_index}: {post.title}")
            continue

        start_time = time.time()  # Capture the start time

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
                "comment": comment.body,
                "url": f"https://reddit.com{comment.permalink}",
                "date": datetime.datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                "score": comment.score
            })

        data_list.append(post_data)

        end_time = time.time()  # Capture the end time
        execution_time = end_time - start_time  # Calculate the execution time

        print(
            f"Data gathering for post {post_index} completed in {execution_time:.2f} seconds.")
        time.sleep(0.6)

    df = pd.DataFrame(data_list)

    return df


# main function calls
subreddit_url = input("Sub-Reddit URL: ")
df = scrape_subreddit_hot(subreddit_url, 100)

filename = "reddit_data_{}.json".format(str(time.time()))

# Convert DataFrame to JSON string with indents
json_str = json.dumps(df.to_dict(orient='records'), indent=4)

# Write JSON string to file
with open(filename, 'w') as f:
    f.write(json_str)
