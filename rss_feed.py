import asyncio
import feedparser
from config import RSS_FEEDS

async def fetch_rss_feed():
    loop = asyncio.get_event_loop()
    all_entries = []
    for feed_url in RSS_FEEDS:
        feed = await loop.run_in_executor(None, feedparser.parse, feed_url)
        all_entries.extend([entry.link for entry in feed.entries])
    return all_entries