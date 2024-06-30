import os
import yaml
from datetime import datetime
import re

def create_output_folder(output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

def save_to_yaml(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True, sort_keys=False, default_flow_style=False)
        
def load_from_yaml(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            if isinstance(data, list):
                return {item['url']: item for item in data if 'url' in item}
            return data
    return {}

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