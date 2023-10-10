import os
import time
import datetime
import uuid
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import praw
from config import config
from sqlalchemy import distinct, create_engine
from sqlalchemy.orm import sessionmaker


reddit = praw.Reddit(
    client_id=config["reddit_config"]['client_id'],
    client_secret=config["reddit_config"]['client_secret'],
    user_agent=config["reddit_config"]['user_agent'],
    username=config["reddit_config"]['username'],
    password=config["reddit_config"]['password']
)


# SQLAlchemy Models
Base = declarative_base()


class Post(Base):
    __tablename__ = 'posts'
    id = Column(String, primary_key=True, default=lambda: str(
        uuid.uuid4()), unique=True, nullable=False)
    reddit_id = Column(String)
    subreddit = Column(String)
    title = Column(String)
    selftext = Column(String)
    upvote_ratio = Column(Float)
    ups = Column(Integer)
    downs = Column(Integer)
    score = Column(Integer)
    permalink = Column(String)
    recorded = Column(Integer)


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(String, primary_key=True, default=lambda: str(
        uuid.uuid4()), unique=True, nullable=False)
    reddit_id = Column(String)
    post_id = Column(Integer, ForeignKey('posts.id'))
    author = Column(String)
    comment = Column(Text)
    url = Column(String)
    date = Column(String)
    score = Column(Integer)
    recorded = Column(Integer)
    reddit_id = Column(String)
    vectorized = Column(Boolean, default=False)


def get_all_unique_subreddits(session):
    distinct_subreddits_tuples = session.query(distinct(Post.subreddit)).all()
    distinct_subreddits = [item[0] for item in distinct_subreddits_tuples]
    return distinct_subreddits


def initialize_db(log_it=True):
    connection_url = "sqlite:///{}".format(config["local_db"]["filename"])
    if log_it:
        print("Intilizing SQLite connection: {}".format(connection_url))
    engine = create_engine(connection_url)
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
            "reddit_id": str(post.id),
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
            # Ignore deleted or removed comments
            if comment.body == "[deleted]" or comment.body == "[removed]" or comment.author is None:
                continue

            post_data["comments"].append({
                "reddit_id": str(comment.id),
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
    # Get current epoch time as an integer
    current_epoch_time = int(time.time())

    for post_data in data_list:
        # Extract comments from post_data
        comments_data = post_data.pop('comments')

        # Add recorded time to post_data
        post_data["recorded"] = current_epoch_time

        # Check if post with this Reddit ID already exists
        reddit_id = post_data["reddit_id"]
        existing_post = session.query(Post).filter_by(
            reddit_id=reddit_id).first()
        if existing_post:
            print(
                f"Post {reddit_id} already exists in DB, updating comments only.")
            post_id = existing_post.id  # Save for later use in comments
        else:
            print(f"Adding new post {reddit_id} to DB.")
            # Create and save the Post object
            post = Post(**post_data)
            session.add(post)
            session.commit()  # commit here to ensure post.id is populated
            post_id = post.id  # Save for later use in comments

        # Create and save Comment objects
        for comment_data in comments_data:
            # Check if comment with this Reddit ID already exists
            comment_reddit_id = comment_data["reddit_id"]
            existing_comment = session.query(Comment).filter_by(
                reddit_id=comment_reddit_id).first()
            if existing_comment:
                print(f"Comment {comment_reddit_id} already exists, skipping.")
                continue

            print(f"Adding new comment {comment_reddit_id} to DB.")
            comment_data["post_id"] = post_id  # use post_id saved earlier
            # Add recorded time to comment_data
            comment_data["recorded"] = current_epoch_time
            comment = Comment(**comment_data)
            session.add(comment)

        session.commit()

    print("Data saved to database successfully.")


def get_reddit(subreddit_urls, hot_posts_limit):
    for subreddit_url in subreddit_urls:
        hot_posts_limit = int(hot_posts_limit)
        session = initialize_db()
        data_list = scrape_subreddit_hot(
            subreddit_url, hot_posts_limit, session)
        save_to_db(session, data_list)
    return
