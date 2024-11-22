import os
from dotenv import load_dotenv

load_dotenv()


RSS_FEEDS = [
    'https://www.aljazeera.com/xml/rss/all.xml',
    # ad more RSS feed URLs here
]

OUTPUT_FOLDER = 'output'
ARTICLES_FILE = os.path.join(OUTPUT_FOLDER, 'articles.yaml')
SUMMARIES_FILE = os.path.join(OUTPUT_FOLDER, 'summaries.yaml')
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
NEETS_API_KEY = os.getenv("NEETS_API_KEY")
DEFAULT_TTS_PROVIDER = "neets"
DEFAULT_NEETS_MODEL = "ar-diff-50k"
DEFAULT_NEETS_VOICE = "cardi-b"
DEFAULT_ELEVENLABS_VOICE = "d39BbXcI33A814zijpKb"

SUMMARIZER_MODEL = "openrouter/google/gemini-flash-1.5"

SETTINGS_FILE = os.path.join(OUTPUT_FOLDER, 'settings.yaml')

