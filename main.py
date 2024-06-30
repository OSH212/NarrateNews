import os
import asyncio
import argparse
import tkinter as tk
from gui import launch_gui, NarrateNewsGUI
from datetime import datetime
from rss_feed import fetch_rss_feed
from article_extraction import extract_articles
from summarization import summarize_text
from text_to_speech import convert_to_audio, select_tts_provider, select_voice, select_neets_model, fetch_elevenlabs_voices, fetch_neets_voices
from utils import create_output_folder, save_to_yaml, load_from_yaml, filter_today_articles, sanitize_filename
from config import OUTPUT_FOLDER, ARTICLES_FILE, SUMMARIES_FILE, DEFAULT_TTS_PROVIDER, DEFAULT_NEETS_VOICE, DEFAULT_NEETS_MODEL, ELEVENLABS_VOICE_ID
from models import Summary, Article

def main(use_gui=False):
    if use_gui:
        launch_gui_with_defaults()
        return

    asyncio.run(process_feeds())

def launch_gui_with_defaults():
    launch_gui(use_defaults=True)

async def process_feeds():
    create_output_folder(OUTPUT_FOLDER)

    tts_provider = select_tts_provider()
    if tts_provider == DEFAULT_TTS_PROVIDER:
        selected_voice_id = DEFAULT_NEETS_VOICE if tts_provider == "neets" else ELEVENLABS_VOICE_ID
        selected_model = DEFAULT_NEETS_MODEL if tts_provider == "neets" else None
    else:
        # fetch available voices and let the user select one
        if tts_provider == "elevenlabs":
            voices = fetch_elevenlabs_voices()
            selected_voice_id = select_voice(voices) or ELEVENLABS_VOICE_ID
            selected_model = None
        else:  # neets
            voices = fetch_neets_voices()
            selected_voice_id = select_voice(voices) or DEFAULT_NEETS_VOICE
            selected_model = select_neets_model()

    urls = await fetch_rss_feed()
    existing_articles = load_from_yaml(ARTICLES_FILE)
    existing_summaries = load_from_yaml(SUMMARIES_FILE)

    new_urls = [url for url in urls if url not in existing_articles]
    new_articles = await extract_articles(new_urls)
    
    for article in new_articles:
        existing_articles[article.url] = article.__dict__

    save_to_yaml(existing_articles, ARTICLES_FILE)

    today_articles = filter_today_articles([Article(**article_dict) for article_dict in existing_articles.values()])

    for article in today_articles:
        if article.url not in existing_summaries:
            summary_text = summarize_text(article.content)
            safe_title = sanitize_filename(article.title)
            audio_filename = f"{safe_title}.mp3"
            audio_path = os.path.join(OUTPUT_FOLDER, audio_filename)
            
            if not os.path.exists(audio_path):
                convert_to_audio(summary_text, audio_path, tts_provider, selected_voice_id, selected_model)
            
            existing_summaries[article.url] = Summary(article=article, summary=summary_text, audio_path=audio_path).__dict__

    save_to_yaml(existing_summaries, SUMMARIES_FILE)

    print(f"Processed {len(today_articles)} articles. Summaries and audio files saved in {OUTPUT_FOLDER}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NarrateNews")
    parser.add_argument("--gui", action="store_true", help="Launch the GUI")
    args = parser.parse_args()

    asyncio.run(main(use_gui=args.gui))
