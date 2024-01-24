README for NarrateNews: a News Summarization and Audio Conversion Script

Overview

This script is designed to fetch news articles from RSS feeds and HTML pages, summarize them using OpenAI's GPT model, and convert the summaries to audio files using ElevenLabs' text-to-speech API. It is intended for users who prefer to listen to news summaries rather than read full articles.

The idea for NarrateNews was born out of the desire to stay informed and up-to-date with current events without the time-consuming task of reading through every article, by leveraging AI tools to efficiently summarize and audibly deliver key news content

Current Features:

- Fetches news articles from specified RSS feeds and HTML pages.
- Summarizes articles using OpenAI's GPT model.
- Converts summaries to audio files.
- Filters and sorts articles by publishing date.
- Handles user input for the number of articles to process.
- Continuously checks for new articles at a set interval.

Requirements

To run this script, you will need Python 3.x and the following packages:
- requests
- beautifulsoup4
- feedparser
- newspaper3k
- openai


Install the required packages using the following command:
txt

Setup
1. Set up the necessary environment variables:
- OPENAI_API_KEY: Your OpenAI API key.
- ELEVEN_API_KEY: Your ElevenLabs API key.
- ELEVENLABS_VOICE_ID: The voice ID for the desired voice from ElevenLabs.

2. Run the script, execute the main.py file (python3 main.py)

The script will prompt you to enter the number of articles to process or 'All' to process all of today's articles. After processing, the summaries will be saved in the article_summaries.csv file, and the audio files will be saved in the output_audios directory.

Continuous Execution

The script is designed to run continuously, checking for new articles every 3 minutes. To stop the script, use the interrupt command (Ctrl+C) in your terminal.

Error Handling

The script includes error handling to manage issues such as invalid URLs, failed downloads, and API errors. Errors are logged to the console.

Customization

You can customize the script by modifying the RSS feed URL and the list of HTML pages in rss_feed.py. Additionally, you can adjust the text-to-speech settings in text_to_speech.py and the openai model you wish you use.

License

This script is provided as-is under the MIT License. Use it at your own risk.
Support
For support, please open an issue on the GitHub repository where this script is hosted.

Contribution
Contributions are welcome. Please fork the repository, make your changes, and submit a pull request.

Disclaimer
This script uses third-party APIs, and as such, is subject to the terms and conditions of those services. Ensure you comply with their usage policies

Features to come: open-source models, UI, ability to manually input an article url and have it summarized and turned into audio.

Any suggestion, critic, feedback is most welcome. 
