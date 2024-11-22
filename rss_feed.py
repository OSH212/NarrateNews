import asyncio
import feedparser
from config import RSS_FEEDS

async def fetch_rss_feed(rss_feeds):
    loop = asyncio.get_event_loop()
    all_entries = []
    for feed_url in rss_feeds:
        feed = await loop.run_in_executor(None, feedparser.parse, feed_url)
        all_entries.extend([entry.link for entry in feed.entries])
    return all_entries