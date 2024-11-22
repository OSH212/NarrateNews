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
from utils import create_output_folder, save_to_yaml, load_from_yaml, filter_today_articles, sanitize_filename, filter_articles_by_date
from models import Article, Summary

# Global state
processing_task = None
is_processing_paused = False

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
        if os.path.exists(SETTINGS_FILE):
            saved_settings = load_from_yaml(SETTINGS_FILE)
            if saved_settings:
                return Settings(**saved_settings)
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
    
    # Return default settings if loading fails or file doesn't exist
    return Settings(
        ttsProvider=DEFAULT_TTS_PROVIDER,
        voice=DEFAULT_NEETS_VOICE if DEFAULT_TTS_PROVIDER == "neets" else DEFAULT_ELEVENLABS_VOICE,
        neetModel=DEFAULT_NEETS_MODEL,
        summarizerModel=SUMMARIZER_MODEL,
        rssFeeds=RSS_FEEDS,
        autoPlay=False,
        processInterval=300
    )

# Initialize settings from file or defaults
current_settings = load_current_settings()

async def process_articles():
    """Process articles from RSS feeds."""
    try:
        logger.info("Starting article processing")
        
        # Create output folder
        create_output_folder(OUTPUT_FOLDER)
        logger.info(f"Ensuring output folder exists: {OUTPUT_FOLDER}")

        # Load current settings from file
        global current_settings
        current_settings = load_current_settings()
        
        # Use loaded settings
        tts_provider = current_settings.ttsProvider
        voice_id = current_settings.voice
        model = current_settings.neetModel if tts_provider == "neets" else None
        rss_feeds = current_settings.rssFeeds
        
        logger.info(f"Using TTS Provider: {tts_provider}, Voice: {voice_id}, Model: {model}")
        logger.info(f"Processing RSS feeds: {rss_feeds}")

        # Load existing data
        articles_dict = load_from_yaml(ARTICLES_FILE) or {}
        summaries_dict = load_from_yaml(SUMMARIES_FILE) or {}
        logger.info(f"Loaded {len(articles_dict)} existing articles and {len(summaries_dict)} summaries")

        # Fetch new articles
        logger.info("Fetching articles from RSS feeds...")
        urls = await fetch_rss_feed(rss_feeds)
        new_urls = [url for url in urls if url not in articles_dict]
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
                articles_dict[article.url] = article_dict
                
                try:
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
                        provider=tts_provider,  # Using current settings
                        voice_id=voice_id,      # Using current settings
                        model=model            # Using current settings
                    )
                    
                    # Save summary with relative audio path
                    summaries_dict[article.url] = {
                        'article': article_dict,
                        'summary': summary,
                        'audio_path': f"/audio/{audio_filename}"  # Use relative path for API
                    }
                    logger.info(f"Completed processing: {article.title}")
                    
                    # Save after each successful article
                    save_to_yaml(ARTICLES_FILE, articles_dict)
                    save_to_yaml(SUMMARIES_FILE, summaries_dict)
                    logger.info("Saved current progress to files")
                    
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
    logger.info("Fetching current settings")
    return current_settings

@app.post("/settings")
async def update_settings(settings: Settings):
    try:
        logger.info(f"Updating settings: {settings.dict()}")
        global current_settings
        current_settings = settings
        
        # Save settings to file
        save_to_yaml(SETTINGS_FILE, settings.dict())
        logger.info("Settings saved successfully")
        
        return current_settings
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save settings: {str(e)}"
        )

@app.get("/articles")
async def get_articles(filter_date: str = None):
    try:
        logger.info("Fetching articles from storage")
        if not os.path.exists(ARTICLES_FILE):
            logger.warning(f"Articles file not found at {ARTICLES_FILE}")
            return {}
            
        articles = load_from_yaml(ARTICLES_FILE)
        
        if filter_date and articles:
            # Convert string date to date object
            target_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
            articles = filter_articles_by_date(articles, target_date)
            logger.info(f"Filtered articles for date {filter_date}: {len(articles)} articles found")
        
        return articles if articles else {}
    except Exception as e:
        logger.error(f"Error fetching articles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summaries")
async def get_summaries():
    try:
        logger.info("Fetching summaries from storage")
        if not os.path.exists(SUMMARIES_FILE):
            logger.warning(f"Summaries file not found at {SUMMARIES_FILE}")
            return {}
            
        summaries = load_from_yaml(SUMMARIES_FILE)
        logger.info(f"Successfully loaded {len(summaries)} summaries")
        return summaries if summaries else {}
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
