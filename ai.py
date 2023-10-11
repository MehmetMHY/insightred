from langchain.vectorstores import Pinecone
from sqlalchemy import inspect
import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import re
import ast
import json

from reddit import Post, Comment, initialize_db
from config import config
from llm_vm.client import client_build


# extract json from GPT-4 output, or return original text
def extract_json(text):
    lines = text.split("\n")
    json_content = ""
    collect = False

    for line in lines:
        if "```json" in line:
            collect = True
            continue
        elif "```" in line and collect:
            collect = False

        if collect:
            json_content += line

    try:
        obj = ast.literal_eval(json_content)
        return obj
    except (ValueError, SyntaxError):
        return json_content


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


def augment_prompt(vectorstore, query: str, ignore_subreddits=[], time_cutoff=0):
    session = initialize_db()

    if not (isinstance(time_cutoff, int)):
        time_cutoff = 0

    print("Using K={} for similariy search".format(config["rag"]["k"]))

    results = vectorstore.similarity_search(query, k=config["rag"]["k"], filter={
        "subreddit": {
            "$nin": ignore_subreddits
        },
        "time": {
            "$gt": time_cutoff
        }
    })

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


def get_good_comments(product_description, ignore_subreddits, time_cutoff_seconds):
    embed_model = OpenAIEmbeddings(model=config["embedding"]["name"])

    pinecone.init(
        api_key=config["pinecone_db"]["api_key"],
        environment=config["pinecone_db"]["environment"]
    )

    client = client_build(
        type="inference", openai_key=config["rag"]["openai_api_key"], big_model=config["rag"]["main_model"])

    index = pinecone.Index(config["pinecone_db"]["index"])

    # initialize the vector store object
    vectorstore = Pinecone(
        index, embed_model.embed_query, "comment"
    )

    prompt = augment_prompt(vectorstore, product_description,
                            ignore_subreddits, time_cutoff_seconds)

    print("\n")
    print("===> Prompt generated. Now requesting from LLM (this might take a few minutes)...")
    print("\n")

    res = client.complete(prompt=prompt, max_len=1000)

    return extract_json(res)
