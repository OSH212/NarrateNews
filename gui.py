import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import asyncio
import os
from config import *
from rss_feed import fetch_rss_feed
from article_extraction import extract_articles
from summarization import summarize_text
from text_to_speech import convert_to_audio, fetch_elevenlabs_voices, fetch_neets_voices
from utils import create_output_folder, save_to_yaml, load_from_yaml, filter_today_articles, sanitize_filename
from models import Summary, Article

class NarrateNewsGUI:
    def __init__(self, master, use_defaults=False):
        self.master = master
        master.title("NarrateNews")
        master.geometry("800x600")

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both")

        self.create_library_tab()
        self.create_settings_tab()
        self.create_processing_tab()

        if use_defaults:
            self.load_default_settings()
        else:
            self.load_data()
    
    def load_default_settings(self):
        self.tts_provider_var.set(DEFAULT_TTS_PROVIDER)
        self.model_var.set(DEFAULT_NEETS_MODEL)
        self.summarizer_model_var.set(SUMMARIZER_MODEL)
        self.update_voice_options()
        if DEFAULT_TTS_PROVIDER == "neets":
            self.voice_var.set(DEFAULT_NEETS_VOICE)
        else:
            self.voice_var.set(ELEVENLABS_VOICE_ID)
        self.load_data()

    def create_library_tab(self):
        library_frame = ttk.Frame(self.notebook)
        self.notebook.add(library_frame, text="Library")

        self.library_tree = ttk.Treeview(library_frame, columns=("Title", "URL", "Summary", "Audio"), show="headings")
        self.library_tree.heading("Title", text="Title")
        self.library_tree.heading("URL", text="URL")
        self.library_tree.heading("Summary", text="Summary")
        self.library_tree.heading("Audio", text="Audio")
        self.library_tree.pack(expand=True, fill="both")

        self.library_tree.bind("<Double-1>", self.on_item_double_click)

    def create_settings_tab(self):
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")

        ttk.Label(settings_frame, text="TTS Provider:").grid(row=0, column=0, padx=5, pady=5)
        self.tts_provider_var = tk.StringVar(value=DEFAULT_TTS_PROVIDER)
        ttk.Combobox(settings_frame, textvariable=self.tts_provider_var, values=["elevenlabs", "neets"]).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(settings_frame, text="Voice:").grid(row=1, column=0, padx=5, pady=5)
        self.voice_var = tk.StringVar()
        self.voice_combobox = ttk.Combobox(settings_frame, textvariable=self.voice_var)
        self.voice_combobox.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(settings_frame, text="Model:").grid(row=2, column=0, padx=5, pady=5)
        self.model_var = tk.StringVar(value=DEFAULT_NEETS_MODEL)
        self.model_combobox = ttk.Combobox(settings_frame, textvariable=self.model_var, values=["style-diff-500", "vits", "ar-diff-50k"])
        self.model_combobox.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(settings_frame, text="Summarizer Model:").grid(row=3, column=0, padx=5, pady=5)
        self.summarizer_model_var = tk.StringVar(value=SUMMARIZER_MODEL)
        ttk.Entry(settings_frame, textvariable=self.summarizer_model_var).grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(settings_frame, text="Save Settings", command=self.save_settings).grid(row=4, column=0, columnspan=2, pady=10)

        self.tts_provider_var.trace("w", self.update_voice_options)
        self.update_voice_options()

    def create_processing_tab(self):
        processing_frame = ttk.Frame(self.notebook)
        self.notebook.add(processing_frame, text="Processing")

        self.rss_feeds_var = tk.StringVar(value=RSS_FEEDS)
        ttk.Label(processing_frame, text="RSS Feeds (comma-separated):").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(processing_frame, textvariable=self.rss_feeds_var, width=50).grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(processing_frame, text="Process Feeds", command=self.process_feeds).grid(row=1, column=0, columnspan=2, pady=10)

        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(processing_frame, textvariable=self.progress_var).grid(row=2, column=0, columnspan=2, pady=5)

    def update_voice_options(self, *args):
        provider = self.tts_provider_var.get()
        if provider == "elevenlabs":
            voices = fetch_elevenlabs_voices()
        else:
            voices = fetch_neets_voices()
        self.voice_combobox['values'] = [voice[1] for voice in voices]
        self.voice_var.set(voices[0][1] if voices else "")

    def save_settings(self):
        # Update config.py with new settings
        with open("config.py", "r") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.startswith("DEFAULT_TTS_PROVIDER"):
                lines[i] = f'DEFAULT_TTS_PROVIDER = "{self.tts_provider_var.get()}"\n'
            elif line.startswith("DEFAULT_NEETS_MODEL"):
                lines[i] = f'DEFAULT_NEETS_MODEL = "{self.model_var.get()}"\n'
            elif line.startswith("SUMMARIZER_MODEL"):
                lines[i] = f'SUMMARIZER_MODEL = "{self.summarizer_model_var.get()}"\n'

        with open("config.py", "w") as f:
            f.writelines(lines)

        messagebox.showinfo("Settings Saved", "Settings have been updated and saved.")

    def load_data(self):
        existing_summaries = load_from_yaml(SUMMARIES_FILE)
        for url, summary in existing_summaries.items():
            self.library_tree.insert("", "end", values=(summary['article']['title'], url, summary['summary'], summary['audio_path']))


    def on_item_double_click(self, event):
        selection = self.library_tree.selection()
        if not selection:
            return
        item = selection[0]
        audio_path = self.library_tree.item(item, "values")[3]
        if os.path.exists(audio_path):
            os.startfile(audio_path)
        else:
            messagebox.showerror("Error", "Audio file not found.")

    def process_feeds(self):
        self.master.after(0, self.process_feeds_wrapper)

    def process_feeds_wrapper(self):
        asyncio.run(self.process_feeds_async())

    async def process_feeds_async(self):
        self.progress_var.set("Processing feeds...")
        rss_feeds = [feed.strip() for feed in self.rss_feeds_var.get().split(",")]
        
        all_urls = await fetch_rss_feed()

        existing_articles = load_from_yaml(ARTICLES_FILE)
        existing_summaries = load_from_yaml(SUMMARIES_FILE)

        new_urls = [url for url in all_urls if url not in existing_articles]
        new_articles = await extract_articles(new_urls)

        for article in new_articles:
            existing_articles[article.url] = article.__dict__

        save_to_yaml(existing_articles, ARTICLES_FILE)

        today_articles = filter_today_articles([Article(**article_dict) for article_dict in existing_articles.values()])

        for article in today_articles:
            if article.url not in existing_summaries:
                summary_text = summarize_text(article.content)
                safe_title = sanitize_filename(article.title)
                audio_filename = f"{safe_title}.mp3"
                audio_path = os.path.join(OUTPUT_FOLDER, audio_filename)

                if not os.path.exists(audio_path):
                    convert_to_audio(summary_text, audio_path, self.tts_provider_var.get(), self.voice_var.get(), self.model_var.get())

                existing_summaries[article.url] = Summary(article=article, summary=summary_text, audio_path=audio_path).__dict__
                self.library_tree.insert("", "end", values=(article.title, article.url, summary_text, audio_path))

        save_to_yaml(existing_summaries, SUMMARIES_FILE)
        self.progress_var.set(f"Processed {len(today_articles)} articles.")

def launch_gui(use_defaults=False):
    root = tk.Tk()
    app = NarrateNewsGUI(root, use_defaults=use_defaults)
    root.mainloop()