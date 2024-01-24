import csv
from article_extraction import extract_article_content
from summarization import summarize_text
import csv
from newspaper import Article
from summarization import summarize_text
from article_extraction import extract_article_content

csv_file_path = 'article_summaries.csv'
import csv

csv_headers = ['Publishing Date', 'Article URL', 'Summary']

def setup_csv(csv_file_path):
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=csv_headers)
        writer.writeheader()
    return csv_file_path

def write_to_csv(all_article_urls, csv_file_path):
    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=csv_headers)
        
        for article_url in all_article_urls:
            try:
                article_text = extract_article_content(article_url)
                summary = summarize_text(article_text)
                article = Article(article_url)
                article.download()
                article.parse()
                publish_date = article.publish_date.strftime('%Y-%m-%d') if article.publish_date else 'Not Available'

                writer.writerow({
                    'Publishing Date': publish_date,
                    'Article URL': article_url,
                    'Summary': summary
                })

                print(f'Article URL: {article_url}')
                print('Summary:', summary)
                print('-' * 50)
            except Exception as e:
                print(f"An error occurred while processing the URL: {article_url}")
                print(str(e))