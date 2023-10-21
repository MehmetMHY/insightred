<p align="center">
  <img width="300" src="./assets/logo.png">
</p>

## About

**InsightRed** is an LLM-powered tool adept at extracting the latest Reddit comments from subreddits, sorted by "Hot", and pinpointing users who exhibit potential interest in your project or product. It's a Reddit marketing tool to help you get your initial users for your product/project.

This project was build for the ANARCHY October 2023 Hackathon. Checkout ANARCHY on their [website](https://github.com/anarchy-ai) and [github](https://anarchy.ai/welcome/why_anarchy).

## Team Members:

- [Mehmet Yilmaz](https://github.com/MehmetMHY)
- [Ben Zimmerman](https://github.com/T3CH3Y)
- [Ananya Aithal](https://github.com/mysteriousbug)

## Demo:

<div align="center">

[![Demo Video](./assets/thumbnail.png)](https://youtu.be/xhKwnKxmg5k)

*click the image to view the YouTube video or click here: https://youtu.be/xhKwnKxmg5k*

</div>

## How To Setup

1. (OPTIONAL) This is tool is designed for Unix based operating systems (MacOS or Linux). So if you are using Windows, I recommend using Docker. To set that up, do the following:

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

2. Clone this project and cd into it:

   ```
   git clone git@github.com:MehmetMHY/insightred.git
   cd insightred
   ```

3. For this tool, you will need to get these API keys:

   - Reddit API Keys:
     - Why? This is used to scrape data from Reddit
     - How? Watch this [video](https://www.youtube.com/watch?v=FdjVoOf9HN4) from timestamps 00:00 to 03:05. You will also need to grab your Reddit account's username and password.
   - OpenAI API Key
     - Why? To use the GPT-4 LLM model. This can be changed in the config file but by default we use the GPT-4 model.
     - How? Go to [OpenAI's API Page](https://openai.com/blog/openai-api) to setup your account. After this, setup billing for the API by going to this link: https://platform.openai.com/account/billing/overview. With billing setup, create & get the API key from this link: https://platform.openai.com/account/api-keys.
   - Pinecone API Key
     - Why? We use Retrieval Augmented Generation, so we need a vector database. For this, we decided to go with Pinecone as our vector database.
     - How? Go to [Pinecone's Website](https://www.pinecone.io/) & sign up or log in if you already have an account. After you login, you should be in the Pinecone dashboard. From there, make sure you don't create an Index. If you do, delete it because InsightRed will generate the Index for you. Then, go to the "API Keys" tab and click on "Create API Key". Create your API key and save it.

4. Set your environment variables in a file called ".env". Check out the "env_template" file to get an idea of the env file layout. This file should contain the following content (you set your key values):

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

   - Make sure the create and save these values. You will need to source them later on.

5. Install dependencies:

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

6. Make sure to source/activate your environment variables and your python environment:

   ```
   # activate local python environment
   source env/bin/activate

   # source/activate environment variables
   source .env
   ```

7. Run the CLI tool to use this application. Run the following command and fill out ALL of the questions:

   ```
   python3 main.py
   ```

8. When the CLI is running, fill out all the questions. You can skip some of those questions if allowed. After the questions are answered, the tool should output Reddit comments you can reply to for your project/product.

## Credits:

### Notable Outside Credit:

- ChatGPT (GPT-4)
- James Briggs (YouTuber)

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
