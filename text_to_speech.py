import os
import requests
import csv
from utils import create_output_folder
import json


ELEVEN_API_KEY = os.environ.get("ELEVEN_API_KEY")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID")



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
    response = requests.post(url, data=encoded_data, headers=headers)
    if response.status_code == 200:
        with open(output_file_path, 'wb') as f:
            f.write(response.content)
        print(f"Audio saved to {output_file_path}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)