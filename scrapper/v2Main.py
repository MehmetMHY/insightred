import os
import time
import json
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import praw
import pandas as pd

reddit = praw.Reddit(
    client_id=os.environ['CLIENT_ID'],
    client_secret=os.environ['SECRET_KEY'],
    user_agent="MyAPI/0.0.1",
    username=os.environ['ACCOUNT_USERNAME'],
    password=os.environ['ACCOUNT_PASSWORD']
)

# SQLAlchemy Models
Base = declarative_base()


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    subreddit = Column(String)
    title = Column(String)
    selftext = Column(String)
    upvote_ratio = Column(Float)
    ups = Column(Integer)
    downs = Column(Integer)
    score = Column(Integer)
    permalink = Column(String)


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    author = Column(String)
    comment = Column(Text)
    url = Column(String)
    date = Column(String)
    score = Column(Integer)


def initialize_db():
    engine = create_engine('sqlite:///reddit_data.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def scrape_subreddit_hot(subreddit_url, limit=10, session=None):
    subreddit_name = subreddit_url.split('/')[-2]
    subreddit = reddit.subreddit(subreddit_name)
    hot_posts = subreddit.hot(limit=limit)

    data_list = []
    for post_index, post in enumerate(hot_posts, start=1):
        if post.stickied:  # Skip if the post is pinned
            print(f"---> Skipping pinned post {post_index}: {post.title}")
            continue

        if session:
            # Check if post has been scraped previously
            exists = session.query(Post).filter_by(
                permalink=post.permalink).first()
            if exists:
                # Check if there are new comments
                current_comment_count = session.query(
                    Comment).filter_by(post_id=exists.id).count()
                if current_comment_count >= post.num_comments:
                    print(
                        f"---> Skipping post {post_index}: {post.title} as it has no new comments.")
                    continue
                else:
                    print(
                        f"---> Updating post {post_index}: {post.title} for new comments.")
            else:
                print(
                    f"---> Scraping new post {post_index}: {post.title}")

        start_time = time.time()

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

        end_time = time.time()
        execution_time = end_time - start_time

        print(
            f"Data gathering for post {post_index} completed in {execution_time:.2f} seconds.")
        time.sleep(0.6)

    return data_list


def save_to_db(session, data_list):
    for post_data in data_list:
        # Extract comments from post_data
        comments_data = post_data.pop('comments')

        # Create and save the Post object
        post = Post(**post_data)
        session.add(post)
        session.commit()  # commit here to ensure post.id is populated

        # Create and save Comment objects
        for comment_data in comments_data:
            comment_data["post_id"] = post.id
            comment = Comment(**comment_data)
            session.add(comment)

        session.commit()

    print("Data saved to database successfully.")


# main function calls
if __name__ == "__main__":
    subreddit_url = input("Sub-Reddit URL: ")
    session = initialize_db()
    data_list = scrape_subreddit_hot(subreddit_url, 12, session)

    # Save data to SQLite database
    save_to_db(session, data_list)

    # Optionally: Save data to JSON file as well
    filename = f"reddit_data_{str(time.time())}.json"
    json_str = json.dumps(data_list, indent=4)
    with open(filename, 'w') as f:
        f.write(json_str)
