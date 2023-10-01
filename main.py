import tiktoken
import openai
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
Condense the given Reddit post title, content, and comment into a succinct paragraph (max 150 words), optimized for vectorization and querying in a vector database:

TITLE: 
      {title}

CONTENT: 
      {content}

COMMENT: 
      {comment}

Make sure the final succinct paragraph embodies the COMMENT the most and make sure the output only the condensed paragraph
"""
    prompt_token_count = get_token_count(prompt_template, llm_model)

    if prompt_token_count >= token_limit:
        raise Exception("token limit {} is less then prompt_template token count of {}".format(token_limit, prompt_token_count))
    
    prompt = prompt_template.format(title=title, content=content, comment=comment)

    # TODO: remove this after testing!
    print(prompt)

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
    llm_model = "gpt-3.5-turbo-16k"
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

data = load_json("redditset_100.json")
data = data[0]

title = data["postTitle"]
content = data["postContent"]
comment = data["content"]

output = succinct_comment(title, content, comment)
print(output)
