import asyncio
import feedparser
from config import RSS_FEED_URL

async def fetch_rss_feed():
    loop = asyncio.get_event_loop()
    feed = await loop.run_in_executor(None, feedparser.parse, RSS_FEED_URL)
    return [entry.link for entry in feed.entries]