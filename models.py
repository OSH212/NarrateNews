from dataclasses import dataclass
from datetime import datetime

@dataclass
class Article:
    url: str
    title: str
    content: str
    publish_date: datetime

@dataclass
class Summary:
    article: Article
    summary: str
    audio_path: str = None