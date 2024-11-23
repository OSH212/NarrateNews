import sys
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import os
from pathlib import Path
from typing import Optional, List
from datetime import datetime, date
from contextlib import asynccontextmanager
from loguru import logger
from db import Database

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Add parent directory to Python path to import from root
sys.path.append(str(Path(__file__).parent.parent))

# Import all the necessary modules
from config import *
from rss_feed import fetch_rss_feed
from article_extraction import extract_articles
from summarization import summarize_text
from text_to_speech import convert_to_audio, fetch_elevenlabs_voices, fetch_neets_voices
from utils import create_output_folder, sanitize_filename, filter_articles_by_date
from models import Article, Summary

# Global state
processing_task = None
is_processing_paused = False

# Initialize database
db = Database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - don't automatically start processing
    yield
    # Shutdown
    global processing_task
    if processing_task:
        processing_task.cancel()
        try:
            await processing_task
        except asyncio.CancelledError:
            pass

app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/audio", StaticFiles(directory=OUTPUT_FOLDER), name="audio")

# API Models
class Settings(BaseModel):
    ttsProvider: str
    voice: str
    neetModel: str
    summarizerModel: str
    rssFeeds: List[str]
    autoPlay: bool
    processInterval: int = 300

# Modify the settings initialization
def load_current_settings():
    try:
        # Get settings from database, ensuring defaults exist
        settings = db.ensure_default_settings()
        if settings:
            return Settings(**settings)
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        # Return default settings if loading fails
        return Settings(
            ttsProvider=DEFAULT_TTS_PROVIDER,
            voice=DEFAULT_NEETS_VOICE if DEFAULT_TTS_PROVIDER == "neets" else DEFAULT_ELEVENLABS_VOICE,
            neetModel=DEFAULT_NEETS_MODEL,
            summarizerModel=SUMMARIZER_MODEL,
            rssFeeds=RSS_FEEDS,
            autoPlay=False,
            processInterval=300
        )

# Initialize settings from database or defaults
current_settings = load_current_settings()

async def process_articles():
    """Process articles from RSS feeds."""
    try:
        logger.info("Starting article processing")
        
        # Create output folder
        create_output_folder(OUTPUT_FOLDER)
        logger.info(f"Ensuring output folder exists: {OUTPUT_FOLDER}")

        # Load current settings
        settings = db.get_settings()
        
        # Use loaded settings
        tts_provider = settings.get('ttsProvider', DEFAULT_TTS_PROVIDER)
        voice_id = settings.get('voice', DEFAULT_NEETS_VOICE if tts_provider == "neets" else DEFAULT_ELEVENLABS_VOICE)
        model = settings.get('neetModel', DEFAULT_NEETS_MODEL) if tts_provider == "neets" else None
        rss_feeds = settings.get('rssFeeds', RSS_FEEDS)
        
        logger.info(f"Using TTS Provider: {tts_provider}, Voice: {voice_id}, Model: {model}")
        logger.info(f"Processing RSS feeds: {rss_feeds}")

        # Fetch new articles
        logger.info("Fetching articles from RSS feeds...")
        urls = await fetch_rss_feed(rss_feeds)
        existing_articles = db.get_articles()
        new_urls = [url for url in urls if url not in existing_articles]
        logger.info(f"Found {len(urls)} total articles, {len(new_urls)} new articles to process")
        
        if new_urls:
            # Extract new articles
            logger.info("Extracting content from new articles...")
            new_articles = await extract_articles(new_urls)
            logger.info(f"Successfully extracted {len(new_articles)} articles")
            
            # Process each article
            for article in new_articles:
                logger.info(f"Processing article: {article.title}")
                
                # Convert article to dictionary
                article_dict = {
                    'url': article.url,
                    'title': article.title,
                    'content': article.content,
                    'publish_date': article.publish_date.isoformat() if article.publish_date else None
                }
                
                try:
                    # Save article to database
                    db.save_article(article_dict)
                    
                    # Generate summary
                    logger.info(f"Generating summary for: {article.title}")
                    summary = await summarize_text(article.content)
                    
                    # Convert to audio using current settings
                    audio_filename = sanitize_filename(f"{article.title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
                    audio_path = os.path.join(OUTPUT_FOLDER, audio_filename)
                    logger.info(f"Converting summary to audio: {audio_filename}")
                    
                    await convert_to_audio(
                        text=summary,
                        output_file_path=audio_path,
                        provider=tts_provider,
                        voice_id=voice_id,
                        model=model
                    )
                    
                    # Save summary to database
                    db.save_summary(article.url, {
                        'summary': summary,
                        'audio_path': f"/audio/{audio_filename}"
                    })
                    
                    logger.info(f"Completed processing: {article.title}")
                    
                except Exception as e:
                    logger.error(f"Error processing article {article.title}: {str(e)}")
                    continue
            
            logger.info("Article processing completed successfully")
        else:
            logger.info("No new articles to process")
            
    except Exception as e:
        logger.error(f"Error during article processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/settings")
async def get_settings():
    try:
        return db.get_settings()
    except Exception as e:
        logger.error(f"Error fetching settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/settings")
async def update_settings(settings: Settings):
    try:
        db.save_settings(settings.dict())
        return settings
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/articles")
async def get_articles(filter_date: str = None):
    try:
        if filter_date:
            target_date = datetime.strptime(filter_date, '%Y-%m-%d')
            articles = db.get_articles(filter_date=target_date)
        else:
            articles = db.get_articles()
        return articles
    except Exception as e:
        logger.error(f"Error fetching articles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summaries")
async def get_summaries():
    try:
        return db.get_summaries()
    except Exception as e:
        logger.error(f"Error fetching summaries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process")
async def start_processing(background_tasks: BackgroundTasks):
    """Start the article processing task."""
    try:
        logger.info("Starting background article processing task")
        
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        
        # Process articles directly instead of in background
        await process_articles()
        
        return {"status": "success", "message": "Article processing started"}
    except Exception as e:
        logger.error(f"Error starting processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voices/elevenlabs")
async def get_elevenlabs_voices():
    try:
        logger.info("Fetching ElevenLabs voices")
        voices = await fetch_elevenlabs_voices()
        logger.info(f"Found {len(voices)} ElevenLabs voices")
        return voices
    except Exception as e:
        logger.error(f"Error fetching ElevenLabs voices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voices/neets")
async def get_neets_voices():
    try:
        logger.info("Fetching Neets voices")
        voices = await fetch_neets_voices()
        logger.info(f"Found {len(voices)} Neets voices")
        return voices
    except Exception as e:
        logger.error(f"Error fetching Neets voices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
