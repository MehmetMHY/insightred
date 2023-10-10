import os

config = {
    "embedding": {
        "name": "text-embedding-ada-002",
        "token_limit": 8192
    },
    "pinecone_db": {
        "environment": "gcp-starter",
        "index": "areddit",
        "dimension": 1536,
        "metric": "cosine",
        "api_key": os.environ["PINECONE_API_KEY"]
    },
    "reddit_config": {
        "client_id": os.environ['CLIENT_ID'],
        "client_secret": os.environ['SECRET_KEY'],
        "user_agent": "MyAPI/0.0.1",
        "username": os.environ['ACCOUNT_USERNAME'],
        "password": os.environ['ACCOUNT_PASSWORD']
    },
    "rag": {
        "main_model": "gpt4",
        "openai_api_key": os.environ["OPENAI_API_KEY"],
        "k": 7
    },
    "local_db": {
        "type": "SQLite",
        "filename": ".reddit_data.db"
    }
}
