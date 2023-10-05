import json
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Note: Adjust the import statement based on your file and class structure
from reddit import Post, Comment, initialize_db


def object_as_dict(obj):
    return {column.key: getattr(obj, column.key) for column in inspect(obj).mapper.column_attrs}


def retrieve_and_print_data(session):
    # Retrieve all posts from the database
    posts = session.query(Post).all()

    data_list = []
    for post in posts:
        post_data = object_as_dict(post)
        post_data["comments"] = []

        # Retrieve comments related to the post
        comments = session.query(Comment).filter_by(post_id=post.id).all()
        for comment in comments:
            comment_data = object_as_dict(comment)
            post_data["comments"].append(comment_data)

        data_list.append(post_data)

    # Convert data to JSON and print
    json_str = json.dumps(data_list, indent=4)
    print(json_str)


# Initialize DB session
session = initialize_db()

# Call the function to retrieve and print the data
retrieve_and_print_data(session)
