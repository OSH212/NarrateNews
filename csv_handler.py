import csv
import os
import re
from article_extraction import extract_article_content
from summarization import summarize_text
from newspaper import Article
from text_to_speech import convert_to_audio

csv_file_path = 'article_summaries.csv'

csv_headers = ['Publishing Date', 'Article URL', 'Title', 'Summary', 'Audio Identifier']

def has_been_processed(article_url, processed_urls_file='processed_urls.txt'):
    if not os.path.exists(processed_urls_file):
        return False
    with open(processed_urls_file, 'r') as file:
        processed_urls = file.read().splitlines()
    return article_url in processed_urls

def mark_as_processed(article_url, processed_urls_file='processed_urls.txt'):
    with open(processed_urls_file, 'a') as file:
        file.write(article_url + '\n')

def setup_csv(csv_file_path):
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=csv_headers)
        writer.writeheader()
    return csv_file_path

def write_to_csv(all_article_urls, csv_file_path):
    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=csv_headers)
        
        for article_url in all_article_urls:
            if has_been_processed(article_url):
                continue

            try:
                article_text = extract_article_content(article_url)
                summary = summarize_text(article_text)
                article = Article(article_url)
                article.download()
                article.parse()
                title = article.title
                sanitized_title = re.sub(r'[\\/*?:"<>|]', "", title)
                publish_date = article.publish_date.strftime('%Y-%m-%d') if article.publish_date else 'Not Available'
                audio_identifier = f"{sanitized_title}_{publish_date}"

                writer.writerow({
                    'Publishing Date': publish_date,
                    'Article URL': article_url,
                    'Title': title,
                    'Summary': summary,
                    'Audio Identifier': audio_identifier
                })

                output_audio_path = os.path.join('output_audios', f"{audio_identifier}.mp3")
                try:
                    convert_to_audio(summary, output_audio_path)
                except Exception as e:
                    print(f"Error converting summary to audio for URL {article_url}: {e}")

                print(f'Article URL: {article_url}')
                print('Title:', title)
                print('Summary:', summary)
                print('-' * 50)
                
                mark_as_processed(article_url)
            except Exception as e:
                print(f"An error occurred while processing the URL: {article_url}")
                print(str(e))
