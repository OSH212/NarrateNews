import os
import asyncio
import argparse
from datetime import datetime
from rss_feed import fetch_rss_feed
from article_extraction import extract_articles
from summarization import summarize_text
from text_to_speech import convert_to_audio, select_tts_provider, select_voice, select_neets_model
from utils import create_output_folder, sanitize_filename
from config import OUTPUT_FOLDER, DEFAULT_TTS_PROVIDER, DEFAULT_NEETS_VOICE, DEFAULT_NEETS_MODEL, ELEVENLABS_VOICE_ID
from models import Summary, Article
from db import Database

# Initialize database
db = Database()

def main(use_gui=False):
    if use_gui:
        launch_gui_with_defaults()
        return

    asyncio.run(process_feeds())

async def process_feeds():
    create_output_folder(OUTPUT_FOLDER)

    tts_provider = select_tts_provider()
    if tts_provider == DEFAULT_TTS_PROVIDER:
        selected_voice_id = DEFAULT_NEETS_VOICE if tts_provider == "neets" else ELEVENLABS_VOICE_ID
        selected_model = DEFAULT_NEETS_MODEL if tts_provider == "neets" else None
    else:
        if tts_provider == "elevenlabs":
            voices = fetch_elevenlabs_voices()
            selected_voice_id = select_voice(voices) or ELEVENLABS_VOICE_ID
            selected_model = None
        else:  # neets
            voices = fetch_neets_voices()
            selected_voice_id = select_voice(voices) or DEFAULT_NEETS_VOICE
            selected_model = select_neets_model()

    urls = await fetch_rss_feed()
    existing_articles = db.get_articles()
    new_urls = [url for url in urls if url not in existing_articles]
    new_articles = await extract_articles(new_urls)
    
    for article in new_articles:
        article_dict = {
            'url': article.url,
            'title': article.title,
            'content': article.content,
            'publish_date': article.publish_date.isoformat() if article.publish_date else None
        }
        db.save_article(article_dict)

    today_articles = filter_articles_by_date(existing_articles, datetime.now().date())

    for article in today_articles.values():
        if article['url'] not in db.get_summaries():
            summary_text = summarize_text(article['content'])
            safe_title = sanitize_filename(article['title'])
            audio_filename = f"{safe_title}.mp3"
            audio_path = os.path.join(OUTPUT_FOLDER, audio_filename)
            
            if not os.path.exists(audio_path):
                convert_to_audio(summary_text, audio_path, tts_provider, selected_voice_id, selected_model)
            
            db.save_summary(article['url'], {
                'summary': summary_text,
                'audio_path': f"/audio/{audio_filename}"
            })

    print(f"Processed {len(today_articles)} articles. Summaries and audio files saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NarrateNews")
    parser.add_argument("--gui", action="store_true", help="Launch the GUI")
    args = parser.parse_args()

    asyncio.run(main(use_gui=args.gui))
