
# Article Analyzer API

A FastAPI application that analyzes article content using OpenAI's language models to extract a concise **summary** and detect **nationalities** mentioned in the text.


## Demo

http://fastapi-docker-ai-env.eba-e9tnf5p2.ap-southeast-1.elasticbeanstalk.com/docs#/default/health_check_health_get


## Run Locally

Clone the repository:

 ```bash
git clone https://github.com/simingg/fastapi-backend-ai.git
cd fastapi-backend-ai
```
Create the virtual environment:
 ```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```
Install Dependencies
 ```bash
pip install --upgrade pip
pip install -r requirements.txt
```
Run the application
 ```bash
uvicorn application:application --reload
```
## API Reference

####

```
#### Shows OpenAI config and model details.

```http
  GET /health
  
```


```
#### Analyze a text or uploaded article to extract:
        1. A summary

        2. A list of Nationalities and Countries mentioned

```http
  POST /analyze
```
## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`OPENAI_API_KEY`

