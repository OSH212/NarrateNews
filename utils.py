import os
import yaml
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)

def create_output_folder(output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

def save_to_yaml(file_path, data):
    """Save data to a YAML file, creating the directory if it doesn't exist."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save the data
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.safe_dump(data, file, allow_unicode=True, sort_keys=False, default_flow_style=False)
            
        # Verify the file was created and has content
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            raise IOError(f"Failed to create or write to file: {file_path}")
            
        logger.info(f"Successfully saved data to {file_path}")
            
    except Exception as e:
        logger.error(f"Error saving to {file_path}: {str(e)}")
        raise  # Re-raise the exception to be handled by the caller

def load_from_yaml(file_path):
    """Load data from a YAML file."""
    try:
        if not os.path.exists(file_path):
            logger.info(f"File does not exist: {file_path}")
            return None
            
        if os.path.getsize(file_path) == 0:
            logger.warning(f"File is empty: {file_path}")
            return None
            
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            logger.info(f"Successfully loaded data from {file_path}")
            return data
            
    except Exception as e:
        logger.error(f"Error loading from {file_path}: {str(e)}")
        return None

def filter_today_articles(articles):
    today = datetime.now().date()
    return [article for article in articles if article.publish_date.date() == today]

def sanitize_filename(filename):
    # remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # replace spaces w/ underscores
    filename = filename.replace(' ', '_')
    # limit filename length: 200 characters
    return filename[:200]

def filter_articles_by_date(articles, target_date):
    """Filter articles by a specific date."""
    if not articles:
        return {}
    
    filtered = {}
    for url, article in articles.items():
        if article.get('publish_date'):
            article_date = datetime.fromisoformat(article['publish_date']).date()
            if article_date == target_date:
                filtered[url] = article
    
    # Sort by publish date (newest first)
    sorted_articles = dict(sorted(
        filtered.items(),
        key=lambda x: datetime.fromisoformat(x[1]['publish_date']),
        reverse=True
    ))
    
    return sorted_articles