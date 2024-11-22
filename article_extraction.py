import aiohttp
import asyncio
from newspaper import Article as NewsArticle
from tenacity import retry, stop_after_attempt, wait_exponential
from models import Article
from datetime import datetime

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_article(session, url):
    # fetch article content from url
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()

async def extract_article_content(url):
    
    async with aiohttp.ClientSession() as session:
        # fetch html content
        html = await fetch_article(session, url)
        
        # parse article using newspaper3k
        article = NewsArticle(url)
        article.set_html(html)
        article.parse()
        
        title = article.title
        content = article.text
        publish_date = article.publish_date or datetime.now()
        

        return Article(url=url, title=title, content=content, publish_date=publish_date)

async def extract_articles(urls):
    # create tasks for each url
    tasks = [extract_article_content(url) for url in urls]
    # gather results asynchronously
    articles = await asyncio.gather(*tasks)
    # filter out None values and return list of articles
    return [article for article in articles if article is not None]