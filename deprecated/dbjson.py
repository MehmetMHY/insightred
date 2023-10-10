import json
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from reddit import Post, Comment, initialize_db


def object_as_dict(obj):
    return {column.key: getattr(obj, column.key) for column in inspect(obj).mapper.column_attrs}


def retrieve_data(session):
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

    return data_list


# Initialize DB session
session = initialize_db()

# Call the function to retrieve and print the data
data = retrieve_data(session)

filename = ".sqlite_db.json"
with open(filename, 'w') as json_file:
    json.dump(data, json_file, indent=4)

print("Created Sqlite Back: {}".format(filename))
