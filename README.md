NarrateNews: A News Summarization and Audio Conversion Application

Overview

NarrateNews is now a Python application designed to fetch news articles from RSS feeds, summarize them using AI models, and convert the summaries to audio files. It now features a graphical user interface (GUI) for easier interaction and management of the news library.


Current Features:

- Fetches news articles from specified RSS feeds (most RSS feeds work, some edge cases with XML links)
- Summarizes articles using AI models (configurable, default is Gemini Flash 1.5 via OpenRouter).
- Converts summaries to audio files using multiple text-to-speech providers (ElevenLabs and Neets.ai).
- Filters and sorts articles by publishing date.
- GUI for easy management of the news library and settings.
- Audio player integrated into GUI 
- Ability to view article summaries and open original articles from the GUI.
- Continuous processing of feeds with pause/resume functionality.
- Settings management for TTS providers, voices, and models.


To run this script, you will need Python 3.x and the following packages:

tkinter
pygame
requests
feedparser
newspaper3k
litellm
pyyaml
aiohttp


To install: run pip install -r requirements.txt


Setup

1. Create a .env file in your project directory:


OPENAI_API_KEY=
ELEVEN_API_KEY=
ELEVENLABS_VOICE_ID=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
NEETS_API_KEY=-
OPENROUTER_API_KEY=

To start, I suggest a Neets APi key (it's free to start) and an OpenRouter API key (access to most models/providers). 

2. Run the application by executing the main.py file:

   python3.11 main.py --gui

Usage

The application will launch with a graphical interface. You can:

- View and manage your news library in the "Library" tab.
- Adjust settings for TTS providers and models in the "Settings" tab.
- Process new feeds and manage ongoing processing in the "Processing" tab.odel you wish you use.

Customization

You can customize the application by modifying the RSS feeds and default settings in the config.py file.

Please fork the repository, make your changes, and submit a pull request.

Disclaimer

This application uses third-party APIs and services such as ElevenLabs , Neets.ai, OpenAI, etc.. Ensure you comply with their respective usage policies and terms of service.

Suggestions, critiques, or feedback to improve NarrateNews are welcome!

## ~~UPDATE -> complete refactoring on the way with Reader app, library, and more TTS providers and languages (OpenAi, Neets.ai)~~

### UPDATE: 
- app ✅
- New provider (Neets) ✅
- library ✅

# TODO/ADD:
 
- Add different input types: text, files (.pdf, .txt, etc.) 
- cleaning codebase + streamlining
- Enhance visuals
- mobile support ? 
- library search ?
- Tags ?
- Free TTS ?

