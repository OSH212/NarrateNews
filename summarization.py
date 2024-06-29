import os
from dotenv import load_dotenv
from litellm import completion
#from openai import OpenAI

#client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
load_dotenv()

def summarize_text(text):
    response = completion(
        model="gpt-3.5-turbo",
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant who summarizes news articles.'},
            {'role': 'user', 'content': text},
        ]
    )
    return response.choices[0].message.content