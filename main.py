from langchain.embeddings.openai import OpenAIEmbeddings
from config import config
import reddit
import vdb
import ai


def add_to_vector_db():
    model_name = config["embedding"]["name"]
    token_limit = config["embedding"]["token_limit"]
    index_name = config["pinecone_db"]["index"]
    vdb_dimension = config["pinecone_db"]["dimension"]
    vdb_metric = config["pinecone_db"]["metric"]
    embed_model = OpenAIEmbeddings(model=model_name)
    vdb.initilize_pinecone(index_name, vdb_dimension, vdb_metric)
    vdb.vectorize(embed_model, model_name, token_limit, index_name)


def update_data(product_description, ignore_subreddits, time_cutoff_seconds, subreddits, postlimit):
    # collect Reddit data, save to local SQLite database
    try:
        reddit.get_reddit(subreddits, postlimit)
    except Exception as err:
        print("ERROR: {}".format(err))
        return None

    # migrate Reddit data from local SQLite database to vector database (Pinecone)
    try:
        add_to_vector_db()
    except Exception as err:
        print("ERROR: {}".format(err))
        return None

    output = None
    try:
        output = ai.get_good_comments(
            product_description, ignore_subreddits, time_cutoff_seconds)
    except Exception as err:
        output = None

    return output
