import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import asyncio
import os
import queue
from config import *
import webbrowser
import subprocess
import threading
import platform
import pygame
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
        self.processing_paused = False
        self.current_audio = None
        pygame.mixer.init()
        self.progress_queue = queue.Queue()
        self.processing_thread = None

        if use_defaults:
            self.load_default_settings()
        else:
            self.load_data()
            
    def load_data(self):
        existing_summaries = load_from_yaml(SUMMARIES_FILE)
        for url, summary in existing_summaries.items():
            self.library_tree.insert("", "end", values=(summary['article']['title'], url, summary['summary'], summary['audio_path']))
    
    def load_default_settings(self):
        self.tts_provider_var.set(DEFAULT_TTS_PROVIDER)
        self.model_var.set(DEFAULT_NEETS_MODEL)
        self.summarizer_model_var.set(SUMMARIZER_MODEL)
        self.update_voice_options()
        if DEFAULT_TTS_PROVIDER == "neets":
            self.voice_var.set(f"{DEFAULT_NEETS_VOICE} ({DEFAULT_NEETS_VOICE})")
        else:
            elevenlabs_voices = fetch_elevenlabs_voices()
            default_voice = next((v for v in elevenlabs_voices if v[0] == DEFAULT_ELEVENLABS_VOICE), None)
            if default_voice:
                self.voice_var.set(f"{default_voice[1]} ({default_voice[0]})")
        self.rss_feeds_var.set(", ".join(RSS_FEEDS))
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

        button_frame = ttk.Frame(library_frame)
        button_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(button_frame, text="Open Article", command=self.open_article).pack(side="left", padx=5)
        ttk.Button(button_frame, text="View Summary", command=self.view_summary).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Play Audio", command=self.play_audio).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh Library", command=self.refresh_library).pack(side="left", padx=5)

        # Audio player controls
        audio_frame = ttk.Frame(library_frame)
        audio_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(audio_frame, text="Play/Pause", command=self.toggle_play_pause).pack(side="left", padx=5)
        ttk.Button(audio_frame, text="Stop", command=self.stop_audio).pack(side="left", padx=5)
        ttk.Button(audio_frame, text="-5s", command=lambda: self.seek_audio(-5)).pack(side="left", padx=5)
        ttk.Button(audio_frame, text="+5s", command=lambda: self.seek_audio(5)).pack(side="left", padx=5)
        self.loop_var = tk.BooleanVar()
        ttk.Checkbutton(audio_frame, text="Loop", variable=self.loop_var).pack(side="left", padx=5)


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

        self.rss_feeds_var = tk.StringVar(value=", ".join(RSS_FEEDS))
        ttk.Label(processing_frame, text="RSS Feeds (comma-separated):").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(processing_frame, textvariable=self.rss_feeds_var, width=50).grid(row=0, column=1, padx=5, pady=5)

        #ttk.Button(processing_frame, text="Process Feeds", command=self.process_feeds).grid(row=1, column=0, columnspan=2, pady=10)

        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(processing_frame, textvariable=self.progress_var).grid(row=2, column=0, columnspan=2, pady=5)
        ttk.Button(processing_frame, text="Process Feeds", command=self.process_feeds).grid(row=1, column=0, pady=10)
        ttk.Button(processing_frame, text="Pause/Resume", command=self.toggle_processing).grid(row=1, column=1, pady=10)

    def refresh_library(self):
        self.library_tree.delete(*self.library_tree.get_children())
        self.load_data()

    def toggle_processing(self):
        self.processing_paused = not self.processing_paused
        status = "Paused" if self.processing_paused else "Resumed"
        self.progress_var.set(f"Processing {status}")

    def toggle_play_pause(self):
        if self.current_audio:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
        else:
            self.play_audio()

    def stop_audio(self):
        pygame.mixer.music.stop()
        self.current_audio = None

    def seek_audio(self, seconds):
        if self.current_audio:
            current_pos = pygame.mixer.music.get_pos() / 1000  # convert to seconds
            new_pos = max(0, current_pos + seconds)
            pygame.mixer.music.play(start=new_pos)


    def update_voice_options(self, *args):
        provider = self.tts_provider_var.get()
        if provider == "elevenlabs":
            voices = fetch_elevenlabs_voices()
        else:
            voices = fetch_neets_voices()
        self.voice_combobox['values'] = [f"{voice[1]} ({voice[0]})" for voice in voices]
        self.voice_var.set(f"{voices[0][1]} ({voices[0][0]})" if voices else "")

    def save_settings(self):
        
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
        self.view_summary()
        
    def open_article(self):
        selection = self.library_tree.selection()
        if not selection:
            return
        item = selection[0]
        url = self.library_tree.item(item, "values")[1]
        webbrowser.open(url)

    def view_summary(self):
        selection = self.library_tree.selection()
        if not selection:
            return
        item = selection[0]
        title = self.library_tree.item(item, "values")[0]
        summary = self.library_tree.item(item, "values")[2]
        
        summary_window = tk.Toplevel(self.master)
        summary_window.title(f"Summary: {title}")
        summary_window.geometry("600x400")
        
        text_widget = tk.Text(summary_window, wrap="word")
        text_widget.pack(expand=True, fill="both")
        text_widget.insert("1.0", summary)
        text_widget.config(state="disabled")

    def play_audio(self):
        selection = self.library_tree.selection()
        if not selection:
            return
        item = selection[0]
        audio_path = self.library_tree.item(item, "values")[3]
        if os.path.exists(audio_path):
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            self.current_audio = audio_path
        else:
            messagebox.showerror("Error", "Audio file not found.")

            
    def process_feeds(self):
        if self.processing_thread and self.processing_thread.is_alive():
            messagebox.showinfo("Processing", "Feed processing is already in progress.")
            return

        self.processing_thread = threading.Thread(target=self.process_feeds_thread)
        self.processing_thread.start()
        self.master.after(100, self.check_progress_queue)

        
    def process_feeds_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.process_feeds_async())

    async def process_feeds_async(self):
        try:
            self.progress_queue.put(("status", "Processing feeds..."))
            rss_feeds = self.rss_feeds_var.get().strip("[]").replace("'", "").split(",")
            rss_feeds = [feed.strip() for feed in rss_feeds if feed.strip()]
            
            print(f"RSS feeds: {rss_feeds}")  # Debug print
            
            all_urls = await fetch_rss_feed(rss_feeds)
            self.progress_queue.put(("status", f"Found {len(all_urls)} articles"))

            existing_articles = load_from_yaml(ARTICLES_FILE)
            existing_summaries = load_from_yaml(SUMMARIES_FILE)

            new_urls = [url for url in all_urls if url not in existing_articles]
            self.progress_queue.put(("status", f"Processing {len(new_urls)} new articles"))

            new_articles = await extract_articles(new_urls)

            for i, article in enumerate(new_articles):
                if self.processing_paused:
                    self.progress_queue.put(("status", "Processing paused"))
                    while self.processing_paused:
                        await asyncio.sleep(1)
                    self.progress_queue.put(("status", "Processing resumed"))

                existing_articles[article.url] = article.__dict__
                self.progress_queue.put(("status", f"Processed article {i+1}/{len(new_articles)}"))

            save_to_yaml(existing_articles, ARTICLES_FILE)

            today_articles = filter_today_articles([Article(**article_dict) for article_dict in existing_articles.values()])

            for i, article in enumerate(today_articles):
                if self.processing_paused:
                    self.progress_queue.put(("status", "Processing paused"))
                    while self.processing_paused:
                        await asyncio.sleep(1)
                    self.progress_queue.put(("status", "Processing resumed"))

                if article.url not in existing_summaries:
                    summary_text = summarize_text(article.content)
                    safe_title = sanitize_filename(article.title)
                    audio_filename = f"{safe_title}.mp3"
                    audio_path = os.path.join(OUTPUT_FOLDER, audio_filename)

                    if not os.path.exists(audio_path):
                        voice_id = self.voice_var.get().split('(')[-1].strip(')')
                        convert_to_audio(summary_text, audio_path, self.tts_provider_var.get(), voice_id, self.model_var.get())

                    existing_summaries[article.url] = Summary(article=article, summary=summary_text, audio_path=audio_path).__dict__
                    self.progress_queue.put(("add_item", (article.title, article.url, summary_text, audio_path)))

                self.progress_queue.put(("status", f"Processed summary and audio {i+1}/{len(today_articles)}"))

            save_to_yaml(existing_summaries, SUMMARIES_FILE)
            self.progress_queue.put(("status", f"Completed processing {len(today_articles)} articles"))
        except Exception as e:
            print(f"Error in process_feeds_async: {str(e)}")  # Debug print
            self.progress_queue.put(("error", str(e)))

    def check_progress_queue(self):
        try:
            while True:
                message = self.progress_queue.get_nowait()
                if message[0] == "status":
                    self.progress_var.set(message[1])
                elif message[0] == "add_item":
                    self.library_tree.insert("", "end", values=message[1])
                elif message[0] == "error":
                    messagebox.showerror("Error", message[1])
        except queue.Empty:
            pass
        
        if self.processing_thread and self.processing_thread.is_alive():
            self.master.after(100, self.check_progress_queue)
        else:
            self.progress_var.set("Ready")
            if self.loop_var.get() and self.current_audio:
                self.play_next_audio()

    def play_next_audio(self):
        current_selection = self.library_tree.selection()
        if current_selection:
            current_index = self.library_tree.index(current_selection[0])
            next_item = self.library_tree.get_children()[current_index + 1]
            self.library_tree.selection_set(next_item)
            self.play_audio()
        else:
            self.stop_audio()


def launch_gui(use_defaults=False):
    root = tk.Tk()
    app = NarrateNewsGUI(root, use_defaults=use_defaults)
    root.mainloop()