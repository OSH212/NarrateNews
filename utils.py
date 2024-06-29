import os
from datetime import datetime
from newspaper import Article
import requests


def create_output_folder(output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)


def is_valid_url(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.RequestException:
        return False

def filter_and_sort_articles(all_article_urls, number_or_all):
    
    today = datetime.now().date()
    todays_articles = []

    
    for url in all_article_urls:
        if not is_valid_url(url):
            continue 

        article = Article(url)
        try:
            article.download()
            article.parse()
        except ArticleException as e:
            print(f"An error occurred while processing the URL: {url}")
            print(str(e))
            continue  # Skip articles that cannot be downloaded or parsed

        
        publish_date = article.publish_date.date() if article.publish_date else None
        if publish_date == today:
            todays_articles.append((publish_date, url))

    
    sorted_articles = sorted(todays_articles, key=lambda x: x[0], reverse=True)

    
    if number_or_all == 'all':
        return [url for _, url in sorted_articles]
    
    else:
        return [url for _, url in sorted_articles[:number_or_all]]
