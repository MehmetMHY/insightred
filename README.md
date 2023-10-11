# InsightRed

## About

An LLM-powered tool adept at extracting the latest Reddit comments from subreddits, sorted by "Hot", and pinpointing users who exhibit potential interest in your project or product. It's a Reddit marketing tool to help you get your initial users for your product/project.

## How To Setup

0. (OPTIONAL) This is tool is designed for Unix based operating systems (MacOS or Linux). So if you are using Windows, I recommend using Docker. To set that up, do the following:

   1. Install Docker: https://docs.docker.com/engine/install/
   2. Grab an Ubuntu install:
      ```
      docker pull ubuntu
      ```
   3. Run, and go into, the Ubuntu image:
      ```
      docker run -it ubuntu
      ```
   4. In the image, install these things:
      ```
      apt update
      apt upgrade
      apt install vim
      apt install git
      apt install python3-pip
      ```

1. Install dependencies:

   ```
   # create local python environment
   python3 -m venv env

   # activate local python environment
   source env/bin/activate

   # install python dependencies
   pip3 install -r requirements.txt

   # install LLM-VM
   git clone https://github.com/anarchy-ai/LLM-VM.git
   cd LLM-VM
   pip3 install .
   cd ..
   ```

2. Set your environment variables in a file called ".env". Check out the "env_template" file to get an idea of the env variables needed. This file should contain the following content (you set your key values):

   ```
   # reddit bot keys
   export CLIENT_ID=""
   export SECRET_KEY=""
   export ACCOUNT_USERNAME=""
   export ACCOUNT_PASSWORD=""

   # OpenAI API key
   export OPENAI_API_KEY=""

   # Pinecone API key
   export PINECONE_API_KEY=""
   ```

   - Checkout

3. Make sure to source/activate your environment variables and your python environment:

   ```
   source .env
   ```

4. Run the CLI tool to use this application. Run the following command and fill out ALL of the questions:
   ```
   python3 main.py
   ```

## Credits:

### Notable Credit:

- ChatGPT (GPT-4)
- James Briggs (YouTube)

### LLM + RAG:

- https://docs.pinecone.io/docs/metadata-filtering
- https://www.youtube.com/watch?v=LhnCsygAvzY

### Reddit Scrapper:

- https://openai.com/blog/openai-api
- https://docs.pinecone.io/docs/overview
- https://www.reddit.com/r/redditdev/comments/14nbw6g/updated_rate_limits_going_into_effect_over_the/
- https://www.reddit.com/prefs/apps
- https://www.youtube.com/watch?v=FdjVoOf9HN4
- https://medium.com/analytics-vidhya/scraping-reddit-data-using-reddit-api-3eba4bd7a56a
- https://gist.github.com/davestevens/4257bbfc82b1e59eeec7085e66314215
- https://github.com/praw-dev/praw
- https://chat.openai.com/
