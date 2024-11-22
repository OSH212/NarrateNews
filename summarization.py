from config import SUMMARIZER_MODEL
from litellm import acompletion

async def summarize_text(text):
    """Generate a summary of the given text using LiteLLM."""
    response = await acompletion(
        model="openrouter/google/gemini-flash-1.5",
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant who summarizes news articles. You output a concise yet comprehensive summary of the given article(s), with no added comments.'},
            {'role': 'user', 'content': text},
        ]
    )
    return response.choices[0].message.content