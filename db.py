import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, Dict, Any
import json
from loguru import logger
from config import (
    DEFAULT_TTS_PROVIDER,
    DEFAULT_NEETS_VOICE,
    DEFAULT_NEETS_MODEL,
    DEFAULT_ELEVENLABS_VOICE,
    SUMMARIZER_MODEL,
    RSS_FEEDS
)

class Database:
    def __init__(self, db_path: str = "narrate_news.db"):
        self.db_path = db_path
        self.init_db()

    @contextmanager
    def get_db(self):
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """Initialize database with required tables and default settings."""
        with self.get_db() as conn:
            # Articles table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    url TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    publish_date TIMESTAMP NOT NULL
                )
            """)
            
            # Summaries table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS summaries (
                    article_url TEXT PRIMARY KEY,
                    summary TEXT NOT NULL,
                    audio_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_url) REFERENCES articles(url)
                )
            """)
            
            # Settings table - stores as key-value pairs
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # Create indices for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_date ON articles(publish_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_summaries_created ON summaries(created_at)")
            
            conn.commit()
        
        # Ensure default settings exist
        self.ensure_default_settings()

    def ensure_default_settings(self):
        """Ensure default settings exist in database."""
        try:
            settings = self.get_settings()
            if not settings:
                default_settings = {
                    'ttsProvider': DEFAULT_TTS_PROVIDER,
                    'voice': DEFAULT_NEETS_VOICE if DEFAULT_TTS_PROVIDER == "neets" else DEFAULT_ELEVENLABS_VOICE,
                    'neetModel': DEFAULT_NEETS_MODEL,
                    'summarizerModel': SUMMARIZER_MODEL,
                    'rssFeeds': RSS_FEEDS,
                    'autoPlay': False,
                    'processInterval': 300
                }
                self.save_settings(default_settings)
                logger.info("Default settings initialized in database")
            return settings
        except Exception as e:
            logger.error(f"Error ensuring default settings: {str(e)}")
            raise

    def save_article(self, article_dict: Dict[str, Any]) -> None:
        """Save article to database."""
        with self.get_db() as conn:
            try:
                # Convert ISO format string to datetime if needed
                publish_date = article_dict['publish_date']
                if isinstance(publish_date, str):
                    publish_date = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))

                conn.execute("""
                    INSERT OR REPLACE INTO articles (url, title, content, publish_date)
                    VALUES (?, ?, ?, ?)
                """, (
                    article_dict['url'],
                    article_dict['title'],
                    article_dict['content'],
                    publish_date
                ))
                conn.commit()
            except Exception as e:
                logger.error(f"Error saving article {article_dict.get('url')}: {str(e)}")
                raise

    def save_summary(self, url: str, summary_dict: Dict[str, Any]) -> None:
        """Save summary to database."""
        with self.get_db() as conn:
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO summaries (article_url, summary, audio_path)
                    VALUES (?, ?, ?)
                """, (
                    url,
                    summary_dict['summary'],
                    summary_dict['audio_path']
                ))
                conn.commit()
            except Exception as e:
                logger.error(f"Error saving summary for {url}: {str(e)}")
                raise

    def save_settings(self, settings_dict: Dict[str, Any]) -> None:
        """Save settings to database."""
        with self.get_db() as conn:
            try:
                # Convert lists and complex types to JSON strings
                for key, value in settings_dict.items():
                    if isinstance(value, (list, dict)):
                        value = json.dumps(value)
                    conn.execute("""
                        INSERT OR REPLACE INTO settings (key, value)
                        VALUES (?, ?)
                    """, (str(key), str(value)))
                conn.commit()
            except Exception as e:
                logger.error(f"Error saving settings: {str(e)}")
                raise

    def get_articles(self, filter_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get articles, optionally filtered by date."""
        with self.get_db() as conn:
            try:
                if filter_date:
                    cursor = conn.execute("""
                        SELECT * FROM articles 
                        WHERE DATE(publish_date) = DATE(?)
                        ORDER BY publish_date DESC
                    """, (filter_date.isoformat(),))
                else:
                    cursor = conn.execute("SELECT * FROM articles ORDER BY publish_date DESC")
                
                return {
                    row['url']: {
                        'url': row['url'],
                        'title': row['title'],
                        'content': row['content'],
                        'publish_date': row['publish_date'].isoformat()
                    }
                    for row in cursor.fetchall()
                }
            except Exception as e:
                logger.error(f"Error fetching articles: {str(e)}")
                return {}

    def get_summaries(self) -> Dict[str, Any]:
        """Get all summaries with their associated articles."""
        with self.get_db() as conn:
            try:
                cursor = conn.execute("""
                    SELECT 
                        a.url, a.title, a.content, a.publish_date,
                        s.summary, s.audio_path
                    FROM articles a
                    JOIN summaries s ON a.url = s.article_url
                    ORDER BY a.publish_date DESC
                """)
                
                return {
                    row['url']: {
                        'article': {
                            'url': row['url'],
                            'title': row['title'],
                            'content': row['content'],
                            'publish_date': row['publish_date'].isoformat()
                        },
                        'summary': row['summary'],
                        'audio_path': row['audio_path']
                    }
                    for row in cursor.fetchall()
                }
            except Exception as e:
                logger.error(f"Error fetching summaries: {str(e)}")
                return {}

    def get_settings(self) -> Dict[str, Any]:
        """Get all settings."""
        with self.get_db() as conn:
            try:
                cursor = conn.execute("SELECT key, value FROM settings")
                settings = {}
                for row in cursor.fetchall():
                    value = row['value']
                    # Try to parse JSON for lists and complex types
                    try:
                        if value.startswith('[') or value.startswith('{'):
                            value = json.loads(value)
                    except json.JSONDecodeError:
                        pass
                    settings[row['key']] = value
                return settings
            except Exception as e:
                logger.error(f"Error fetching settings: {str(e)}")
                return {}

    def migrate_from_yaml(self, articles_yaml: Dict[str, Any], summaries_yaml: Dict[str, Any], settings_yaml: Dict[str, Any]) -> None:
        """Migrate data from YAML files to SQLite database."""
        with self.get_db() as conn:
            try:
                # Start transaction
                conn.execute("BEGIN TRANSACTION")
                
                # Migrate articles
                for url, article in articles_yaml.items():
                    self.save_article(article)
                
                # Migrate summaries
                for url, summary in summaries_yaml.items():
                    self.save_summary(url, summary)
                
                # Migrate settings
                self.save_settings(settings_yaml)
                
                # Commit transaction
                conn.commit()
                logger.info("Successfully migrated data from YAML to SQLite")
            except Exception as e:
                conn.rollback()
                logger.error(f"Error during migration: {str(e)}")
                raise

def create_migration_script():
    """Create a migration script to move from YAML to SQLite."""
    from utils import load_from_yaml
    from config import ARTICLES_FILE, SUMMARIES_FILE, SETTINGS_FILE
    
    def migrate():
        try:
            # Initialize database
            db = Database()
            
            # Load YAML files
            articles = load_from_yaml(ARTICLES_FILE) or {}
            summaries = load_from_yaml(SUMMARIES_FILE) or {}
            settings = load_from_yaml(SETTINGS_FILE) or {}
            
            # Migrate data
            db.migrate_from_yaml(articles, summaries, settings)
            
            logger.info("Migration completed successfully")
            return True
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            return False

    return migrate

if __name__ == "__main__":
    # Create and run migration
    migrate = create_migration_script()
    success = migrate()
    if success:
        print("Migration completed successfully")
    else:
        print("Migration failed. Check logs for details")
