import tiktoken
import openai
import time
import json
import os

def load_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def save_json(data_dict, file_path):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data_dict, json_file, indent=4)

# get the number of tokens in a string for a specific OpenAI model
def get_token_count(string: str, model: str) -> int:
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def create_prompt(title: str, content: str, comment: str, llm_model: str, token_limit: int) -> str:    
    prompt_template = """

Here is the title, content, and a comment for a Reddit post:

TITLE: 
      {title}

CONTENT: 
      {content}

COMMENT: 
      {comment}

Knowing this, do the following:
1. Create a succinct pargraph (max 150) words of the TITLE and CONTENT
2. IF the comment is too long, summarize does to a max of 150 words
3. Combine the final results into this format:
```
COMMENT: <final reddit comment after step #2> POST: <final post data from step #1>
```

Make sure to optmize the final result for vectorization and querying from a vectordatabase. And, make sure your output is ONLY the final output from step #3. DO NOT add additional context/information.
"""
    prompt_token_count = get_token_count(prompt_template, llm_model)

    if prompt_token_count >= token_limit:
        raise Exception("token limit {} is less then prompt_template token count of {}".format(token_limit, prompt_token_count))
    
    prompt = prompt_template.format(title=title, content=content, comment=comment)

    # TODO: remove this after testing!
    print("\n---> Requesting following prompt from model {}:\n```{}\n``` \n".format(llm_model, prompt))

    token_count = get_token_count(prompt, llm_model)
    while token_count > token_limit:
        # trim content if it's longer than the title
        if len(content.split()) > len(title.split()):
            content = " ".join(content.split()[:-1])
        else:
            title = " ".join(title.split()[:-1])
        
        prompt = prompt_template.format(title=title, content=content, comment=comment)
        token_count = get_token_count(prompt, llm_model)
    
    return prompt

def succinct_comment(title, content, comment):
    llm_model = "gpt-3.5-turbo"
    token_limit = 4097 # https://platform.openai.com/docs/models/
    prompt = create_prompt(title, content, comment, llm_model, token_limit)
    completion = openai.ChatCompletion.create(
        model=llm_model ,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    results = completion["choices"][0]["message"]["content"]
    return results

##### MAIN FUNCTION CALLS

openai.api_key = os.getenv("OPENAI_API_KEY").strip("\n")

all_data = load_json("redditset_100.json")

# # TODO: remove after testing
# all_data = [all_data[50]]

start_time = time.time()

index = 1
for data in all_data:
    try:
        if "[removed]" not in data["content"]:
            title = data["postTitle"].replace("\n", "")
            content = data["postContent"].replace("\n", "")
            comment = data["content"].replace("\n", "")
            data["succinctContent"] = succinct_comment(title, content, comment)
        else:
            data["succinctContent"] = ""
    except:
        data["succinctContent"] = ""
    print("{} / {}".format(index, len(all_data)))
    index += 1

runtime = time.time() - start_time

save_json(all_data, "redditSetGPT.json")

print("{} seconds.".format(runtime))