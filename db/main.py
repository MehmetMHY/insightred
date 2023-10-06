from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Pinecone
from sqlalchemy import create_engine, inspect
import os
import pinecone
import time
from langchain.embeddings.openai import OpenAIEmbeddings
import re
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
import json

from reddit import Post, Comment, initialize_db


def object_as_dict(obj):
    return {column.key: getattr(obj, column.key) for column in inspect(obj).mapper.column_attrs}


def create_prompt(all_post, comment_content):
    succinct_content = "COMMENT: {} POST: {}".format(
        comment_content,
        all_post
    )
    return succinct_content


def clean_str(content):
    s = content.replace("\n", "")
    s = re.sub(' +', ' ', s)
    s = s.strip()
    return s


def augment_prompt(query: str, post_about):
    session = initialize_db()

    query = "COMMENT: {} POST: {}".format(query, post_about)

    # get top 3 results from knowledge base
    results = vectorstore.similarity_search(query, k=10)
    # get the text from the results
    source_knowledge = ""
    i = 1
    for x in results:
        comment_id = x.page_content

        unvectorized_comments = session.query(
            Comment).filter_by(id=comment_id).all()

        comment_dict = [object_as_dict(comment)
                        for comment in unvectorized_comments][0]

        post = session.query(Post).filter_by(
            id=comment_dict["post_id"]).first()

        comment_dict["postData"] = object_as_dict(post)

        post_title = clean_str(comment_dict["postData"]["title"])
        post_content = clean_str(comment_dict["postData"]["selftext"])
        comment_content = clean_str(comment_dict["comment"])

        all_post = "{}. {}".format(post_title, post_content)

        content = create_prompt(all_post, comment_content)
        url = clean_str(comment_dict["url"])
        if i != len(results) - 1:
            source_knowledge += "{}) {} URL: {}\n\n".format(i, content, url)
        else:
            source_knowledge += "{}) {} URL: {}".format(i, content, url)
        i += 1

    # feed into an augmented prompt
    augmented_prompt = f"""
Given the Reddit Posts, Comment, & URLs below:
```
{source_knowledge}
```

And the description of the product/project:
```
{query}
```

Identify the comments where the user demonstrates a strong interest or need that aligns closely with the described product/project. The match should be precise; avoid broad interpretations.

Output the results in the following JSON format: an array of objects, where each object contains the comment, post, and url. 

```json
[
  {{
    "comment": "Sample Comment",
    "post": "Sample Post Title or Content",
    "url": "Sample URL"
  }},
  ...
]
```
    """

    return augmented_prompt


embed_model = OpenAIEmbeddings(model="text-embedding-ada-002")

pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"],
    environment='gcp-starter'
)

chat = ChatOpenAI(
    openai_api_key=os.environ["OPENAI_API_KEY"],
    model='gpt-4'
)

index_name = "areddit"

index = pinecone.Index(index_name)

text_field = "commentID"  # the metadata field that contains our text

# initialize the vector store object
vectorstore = Pinecone(
    index, embed_model.embed_query, text_field
)


print()
query = input("Product Description:\n")
post_about = input("POST ABOUT: ")
print()

prompt = HumanMessage(
    content=augment_prompt(query, post_about)
)

messages = [prompt]

res = chat(messages)

print("OUTPUT:")
print(res.content)
