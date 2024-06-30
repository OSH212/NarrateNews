from config import SUMMARIZER_MODEL
from litellm import completion



def summarize_text(text):
    response = completion(
        model="openrouter/google/gemini-flash-1.5",
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant who summarizes news articles. You output a concive yet comprehensive summary of the given article(s), with no added comments.'},
            {'role': 'user', 'content': text},
        ]
    )
    return response.choices[0].message.content