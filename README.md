NarrateNews: A News Summarization and Audio Conversion Application

## Overview

NarrateNews is a modern web application designed to fetch news articles from RSS feeds, summarize them using AI models, and convert the summaries to audio files. It features a modern web interface for easy interaction and management of your news library.

## Screenshots


![Library View](docs/library.png)
![Player View](docs/player.png)

## Current Features

- Fetches news articles from specified RSS feeds
- Summarizes articles using AI models (configurable, default is Gemini Flash 1.5 via OpenRouter)
- Converts summaries to audio files using multiple text-to-speech providers (ElevenLabs and Neets.ai)
- UI:
  - Library 
  - Audio player
  - Settings

## Setup

1. Create a `.env` file in your project directory:


- OPENAI_API_KEY=
- ELEVEN_API_KEY=
- ELEVENLABS_VOICE_ID=
- ANTHROPIC_API_KEY=
- OPENAI_API_KEY=
- NEETS_API_KEY=-
- OPENROUTER_API_KEY=

To start, Use your [ElevenLabs](https://elevenlabs.io/) or a [Neets API key](https://neets.ai/) (it's free to start) and an [OpenRouter API key](https://openrouter.ai/) (access to most models/providers).


2. Install Python dependencies: 
```
pip install -r requirements.txt
```
3. Install Node.js dependencies: 
```
cd narrate-news-web
npm install
```

## Running the application: 
```
python start.py
```

This will start both the API server and web interface. The application will be available at:
- Web UI: http://localhost:3000
- API: http://localhost:8000

## Customization

You can customize the application by:
- Modifying RSS feeds in `config.py`
- Adjusting default settings in `config.py`
- Customizing the web interface in the `narrate-news-web` directory

## Disclaimer

This application uses third-party APIs and services (ElevenLabs, Neets.ai, OpenAI, etc.). Ensure you comply with their respective usage policies and terms of service.

## Contributing

Please fork the repository, make your changes, and submit a pull request.

## TODO/ADD
- different input types
- library search 
- free TTS 
- mobile support
- GraphRAG











## License

MIT-NC License

Copyright (c) 

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, and distribute the Software, subject to the following conditions:

1. The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

2. The Software may not be used for commercial purposes. Commercial purposes include, but are not limited to:
   - Using the Software for commercial advantage or monetary compensation
   - Integrating the Software into a commercial product or service
   - Using the Software in a business environment

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


