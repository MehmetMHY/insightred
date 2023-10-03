import json
import pandas as pd
from langchain.embeddings.openai import OpenAIEmbeddings
import os
import pinecone
import time

embed_model = OpenAIEmbeddings(model="text-embedding-ada-002")

pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"],
    environment='gcp-starter'
)


def load_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


index_name = 'llama-2-rag'

if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        index_name,
        dimension=1536,
        metric='cosine'
    )
    # wait for index to finish initialization
    while not pinecone.describe_index(index_name).status['ready']:
        time.sleep(1)

index = pinecone.Index(index_name)

data = pd.read_json("testDB.json", orient='records')

batch_size = 100
for i in range(0, len(data), batch_size):
    i_end = min(len(data), i + batch_size)
    batch = data.iloc[i:i_end]
    ids = [x['commentID'] for _, x in batch.iterrows()]
    texts = [x['succinctContent'] for _, x in batch.iterrows()]
    # Embed text
    embeds = embed_model.embed_documents(texts)
    # Get metadata to store
    metadata = [
        {'postTitle': x['postTitle'],
         'postAuthor': x['postAuthor'],
         'subreddit': x['subreddit'],
         'postURL': x['postURL'],
         'postCreatedAt': x['postCreatedAt'],
         'postID': x['postID'],
         'commentID': x['commentID'],
         'author': x['author'],
         'createdAt': x['createdAt'],
         'text': x['content'],
         'succinctContent': x['succinctContent'],
         'url': x['url']} for _, x in batch.iterrows()
    ]
    # Add to Pinecone
    index.upsert(vectors=zip(ids, embeds, metadata))
