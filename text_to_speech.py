import os
import json
from loguru import logger
import aiohttp
from config import ELEVEN_API_KEY, ELEVENLABS_VOICE_ID, NEETS_API_KEY, DEFAULT_TTS_PROVIDER, DEFAULT_NEETS_MODEL, DEFAULT_NEETS_VOICE

if not ELEVEN_API_KEY:
    logger.error("Missing required ELEVEN_API_KEY. Please check your .env file.")
    raise ValueError("Missing required ELEVEN_API_KEY")

if not NEETS_API_KEY:
    logger.error("Missing required NEETS_API_KEY. Please check your .env file.")
    raise ValueError("Missing required NEETS_API_KEY")

# fetch available voices from elevenlabs
async def fetch_elevenlabs_voices():
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": ELEVEN_API_KEY}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                voices = await response.json()
                return [(voice["voice_id"], voice["name"]) for voice in voices["voices"]]
    except (aiohttp.ClientError, KeyError) as e:
        logger.error(f"Failed to fetch ElevenLabs voices: {e}")
        return []

# fetch available voices from neets
async def fetch_neets_voices():
    url = "https://api.neets.ai/v1/voices"
    headers = {"accept": "application/json", "X-API-Key": NEETS_API_KEY}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                voices = await response.json()
                return [(voice["id"], voice["title"], ", ".join(voice["supported_models"])) for voice in voices]
    except (aiohttp.ClientError, KeyError) as e:
        logger.error(f"Failed to fetch Neets voices: {e}")
        return []

# prompt user to select tts provider
def select_tts_provider():
    while True:
        choice = input("Select TTS provider (1 for ElevenLabs, 2 for Neets, or press ENTER for default): ").strip()
        if choice == "" or choice == "0":
            return DEFAULT_TTS_PROVIDER
        elif choice in ["1", "2"]:
            return "elevenlabs" if choice == "1" else "neets"
        print("Invalid choice. Please try again.")

# prompt user to select voice
def select_voice(voices):
    print("Available voices:")
    for i, (id, name, info) in enumerate(voices, 1):
        print(f"{i}. {name} ({info})")
    
    while True:
        try:
            choice = input("Select a voice number (or press ENTER for default): ").strip()
            if choice == "" or choice == "0":
                return None
            choice = int(choice)
            if 1 <= choice <= len(voices):
                return voices[choice-1][0]
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number or press ENTER for default.")

# prompt user to select neets model
def select_neets_model():
    models = ["style-diff-500", "vits", "ar-diff-50k"]
    print("Available Neets models:")
    for i, model in enumerate(models, 1):
        print(f"{i}. {model}")
    
    while True:
        try:
            choice = input("Select a model number (or press ENTER for default): ").strip()
            if choice == "" or choice == "0":
                return DEFAULT_NEETS_MODEL
            choice = int(choice)
            if 1 <= choice <= len(models):
                return models[choice-1]
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number or press ENTER for default.")

# convert text to audio using elevenlabs api
async def convert_to_audio_elevenlabs(text, output_file_path, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    encoded_data = json.dumps(data).encode('utf-8')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=encoded_data, headers=headers) as response:
                response.raise_for_status()
                content = await response.read()
                with open(output_file_path, 'wb') as f:
                    f.write(content)
                logger.info(f"Audio saved to {output_file_path}")
                return output_file_path
    except (aiohttp.ClientError, IOError) as e:
        logger.error(f"Error in convert_to_audio_elevenlabs: {e}")
        raise

# convert text to audio using neets api
async def convert_to_audio_neets(text, output_file_path, model, voice_id):
    url = "https://api.neets.ai/v1/tts"
    headers = {
        "accept": "audio/wav",
        "content-type": "application/json",
        "X-API-Key": NEETS_API_KEY
    }
    payload = {
        "params": {"model": model},
        "fmt": "mp3",
        "voice_id": voice_id,
        "text": text
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                response.raise_for_status()
                content = await response.read()
                with open(output_file_path, 'wb') as f:
                    f.write(content)
                logger.info(f"Audio saved to {output_file_path}")
                return output_file_path
    except (aiohttp.ClientError, IOError) as e:
        logger.error(f"Error in convert_to_audio_neets: {e}")
        raise

# main function to convert text to audio
async def convert_to_audio(text, output_file_path, provider, voice_id, model=None):
    if provider == "elevenlabs":
        return await convert_to_audio_elevenlabs(text, output_file_path, voice_id)
    else:  # neets
        return await convert_to_audio_neets(text, output_file_path, model, voice_id)