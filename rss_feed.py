import feedparser
from article_extraction import extract_article_urls

html_urls = [
    'https://www.aljazeera.com/tag/business-and-economy/',
    'https://www.aljazeera.com/tag/climate/',
    'https://www.aljazeera.com/tag/politics/',
    'https://www.aljazeera.com/tag/explainer/',
    'https://www.aljazeera.com/tag/military/',
    'https://www.aljazeera.com/tag/financial-markets/'
]

def fetch_rss_feed():
    rss_feed = feedparser.parse('https://www.aljazeera.com/xml/rss/all.xml')
    rss_article_urls = [entry.link for entry in rss_feed.entries]
    html_article_urls = []
    for url in html_urls:
        html_article_urls.extend(extract_article_urls(url))
    return list(set(rss_article_urls + html_article_urls))
