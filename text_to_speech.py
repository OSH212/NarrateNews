import os
from dotenv import load_dotenv
import requests
import json
from loguru import logger


ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

if not ELEVEN_API_KEY or not ELEVENLABS_VOICE_ID:
    logger.error("Missing required environment variables. Please check your .env file.")
    raise ValueError("Missing required environment variables")


def convert_to_audio(text, output_file_path):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    encoded_data = json.dumps(data).encode('utf-8')
    try:
        response = requests.post(url, data=encoded_data, headers=headers)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        with open(output_file_path, 'wb') as f:
            f.write(response.content)
        logger.info(f"Audio saved to {output_file_path}")
    except requests.RequestException as e:
        logger.error(f"Network or API request error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
    except IOError as e:
        logger.error(f"File writing error: {e}")

