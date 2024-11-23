import os
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)

def create_output_folder(output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

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
    
    return filtered