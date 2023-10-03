import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Define SQLAlchemy models if not defined in this script
# NOTE: You might want to update the import statement with the correct path and model names.
from v2Main import Post, Comment  

# Initialize DB session
engine = create_engine('sqlite:///reddit_data.db')
Session = sessionmaker(bind=engine)
session = Session()

def retrieve_and_print_data(session):
    # Retrieve all posts from the database
    posts = session.query(Post).all()

    # Retrieve all comments for each post
    data_list = []
    for post in posts:
        post_data = {
            "id": post.id,
            "subreddit": post.subreddit,
            "title": post.title,
            "selftext": post.selftext,
            "upvote_ratio": post.upvote_ratio,
            "ups": post.ups,
            "downs": post.downs,
            "score": post.score,
            "permalink": post.permalink,
            "vectorized": post.vectorized,
            "recorded": post.recorded,
            "comments": []
        }

        # Retrieve comments related to the post
        comments = session.query(Comment).filter_by(post_id=post.id).all()
        for comment in comments:
            comment_data = {
                "author": comment.author,
                "comment": comment.comment,
                "url": comment.url,
                "date": comment.date,
                "score": comment.score,
                "recorded": comment.recorded
            }
            post_data["comments"].append(comment_data)

        data_list.append(post_data)

    # Convert data to JSON and print
    json_str = json.dumps(data_list, indent=4)
    print(json_str)

# Call the function to retrieve and print the data
retrieve_and_print_data(session)

