from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Pinecone
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

def augment_prompt(query: str):
    # get top 3 results from knowledge base
    results = vectorstore.similarity_search(query, k=10)
    # get the text from the results
    source_knowledge = ""
    i = 1
    for x in results:
        content = x.page_content
        content = content.replace('\n', ' ') 
        content = re.sub(' +', ' ', content)
        url = x.metadata["url"]
        if i != len(results) - 1:
            source_knowledge += "{}) {} URL: {}\n\n".format(i, content, url)
        else:
            source_knowledge += "{}) {} URL: {}".format(i, content, url)
        i += 1
    
    # feed into an augmented prompt
    augmented_prompt = f"""
Here are some Reddit Posts and Comments:
```
{source_knowledge}
```

Here is a description of my product/project:
```
{query}
```

Knowing this, select the BEST comments where the user would be VERY interested in using the product/project. Make sure it's an exact match. Don't over stretch it.

For your output, make it json that is an array of objects. Make each object contain the comment, post, and url. Your output should only be a json array!
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

# text_field = "text"  # the metadata field that contains our text
text_field = "succinctContent"  # the metadata field that contains our text

# initialize the vector store object
vectorstore = Pinecone(
    index, embed_model.embed_query, text_field
)


print()
query = input("Product Description:\n")
print()

prompt = HumanMessage(
    content=augment_prompt(query)
)

messages = [prompt]

res = chat(messages)

print(res.content)
