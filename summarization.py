import os
from openai import OpenAI

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def summarize_text(text):
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant who summarizes news articles.'},
            {'role': 'user', 'content': text},
        ]
    )
    return response.choices[0].message.content