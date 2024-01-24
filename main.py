import os
import csv 
from rss_feed import fetch_rss_feed
from csv_handler import setup_csv, write_to_csv, csv_headers
from text_to_speech import convert_to_audio
from utils import create_output_folder, filter_and_sort_articles
import time
from datetime import datetime

def get_user_input():
    while True:
        user_input = input("Enter the number of articles to process ('All' for all today's articles or a number): ")
        if user_input.lower() == 'all':
            return 'all'
        elif user_input.isdigit() and int(user_input) > 0:
            return int(user_input)
        else:
            print("Invalid input. Please enter 'All' or a positive number.")

csv_file_path = 'article_summaries.csv'

setup_csv(csv_file_path)

all_article_urls = fetch_rss_feed()

user_choice = get_user_input()

filtered_sorted_articles = filter_and_sort_articles(all_article_urls, user_choice)

write_to_csv(filtered_sorted_articles, csv_file_path)

output_folder = 'output_audios'
create_output_folder(output_folder)

with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        article_title = row['Article URL'].split('/')[-1]  
        summary = row['Summary']

        valid_title = "".join([c for c in article_title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        output_audio_path = os.path.join(output_folder, f"{valid_title}.mp3")
        convert_to_audio(summary, output_audio_path)


while True:
    time.sleep(180) 
    new_article_urls = fetch_rss_feed()  
    new_filtered_sorted_articles = filter_and_sort_articles(new_article_urls, 'all')
    write_to_csv(new_filtered_sorted_articles, csv_file_path)
    convert_to_audio(csv_file_path, output_folder)