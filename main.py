import pandas as pd
import requests
import json
import os

CLIENT_ID = os.environ['CLIENT_ID']
SECRET_KEY = os.environ['SECRET_KEY']

auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_KEY)

data = {
    "grant_type": "password",
    "username": os.environ['ACCOUNT_USERNAME'],
    "password": os.environ['ACCOUNT_PASSWORD']
}

headers = {"User-Agent": "MyAPI/0.0.1"}

res = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers)

TOKEN = res.json()["access_token"]

headers = {**headers, **{'Authorization': f'bearer {TOKEN}'}}

# res_hot = requests.get('https://oauth.reddit.com/r/python/hot',headers=headers,params={'limit':'50'})
res = requests.get('https://oauth.reddit.com/r/python/new',headers=headers, params={"limit": "100"})

data_list = []
for post in res.json()["data"]["children"]:
    data_list.append({
        "subreddit": post["data"]["subreddit"],
        "title": post["data"]["title"],
        "selftext": post["data"]["selftext"],
        "upvote_ratio": post["data"]["upvote_ratio"],
        "ups": post["data"]["ups"],
        "downs": post["data"]["downs"],
        "score": post["data"]["score"],
        "permalink": post["data"]["permalink"]
    })

df = pd.DataFrame(data_list)

print(df)