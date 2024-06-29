import requests
import re
from newspaper import Article
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def extract_article_content(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text

def extract_article_urls(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    base_url = 'https://www.aljazeera.com'
    article_urls = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href) if not href.startswith('http') else href
        if '/2' in href and href.count('/') >= 2:
            article_urls.append(full_url)
    return article_urls
