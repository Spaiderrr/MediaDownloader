import os
import getpass
import time
import json
import traceback
import threading
from tkinter import filedialog, messagebox
import subprocess
import sys
import requests
import webbrowser
from packaging import version

import yt_dlp
import customtkinter as ctk

ctk.set_appearance_mode("dark")

CONFIG_FILE = "settings.json"

# ----------------------------------------------------------------------
# Класс для всплывающих подсказок (tooltip)
class ToolTip:
    def __init__(self, widget, text_func):
        self.widget = widget
        self.text_func = text_func
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ctk.CTkLabel(tw, text=self.text_func(), justify="left",
                             fg_color="#ffffe0", text_color="black",
                             corner_radius=4, padx=5, pady=2)
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# ----------------------------------------------------------------------
# Менеджер переводов (расширенный)
class LanguageManager:
    def __init__(self):
        self._current_lang = "ru"
        self._strings = {
            "ru": {
                "url_label": "Ссылка на видео или плейлист:",
                "info_btn": "Инфо",
                "login_btn": "Войти в YouTube",
                "folder_btn": "Обзор",
                "folder_path_label": "Путь: {}",
                "audio_radio": "Аудио",
                "video_radio": "Видео",
                "quality_label": "Качество:",
                "fragments_label": "Фрагментов:",
                "audio_format_label": "Аудиоформат:",
                "video_container_label": "Контейнер видео:",
                "playlist_range_label": "Диапазон плейлиста (1-5 или 1,3,5):",
                "status_ready": "Готов к работе",
                "status_cancel": "Отмена...",
                "status_processing": "Постобработка...",
                "status_completed": "Готово!",
                "status_error": "Ошибка! Смотрите лог",
                "download_btn": "НАЧАТЬ СКАЧИВАНИЕ",
                "stop_btn": "СТОП",
                "downloading_btn": "ЗАГРУЗКА...",
                "update_btn": "Проверить обновление",
                "log_label": "Лог загрузки:",
                "no_url_title": "Нет ссылки",
                "no_url_msg": "Введите ссылку на видео или плейлист.",
                "already_downloading": "Загрузка уже выполняется.",
                "complete_title": "Готово",
                "complete_msg": "Файлы сохранены в:\n{}",
                "update_available_title": "Доступно обновление",
                "update_available_msg": "Доступна новая версия yt-dlp: {}\nВаша версия: {}\nОткрыть страницу загрузки?",
                "update_error_title": "Ошибка проверки",
                "update_error_msg": "Не удалось проверить обновления: {}",
                "update_already": "yt-dlp уже обновлен до последней версии {}",
                "cookies_success_title": "Успех",
                "cookies_success_msg": "Куки из {} загружены.\nТеперь можно скачивать 18+ контент.",
                "cookies_error_msg": "Не удалось загрузить куки из {}.\nУбедитесь, что браузер закрыт.",
                "cookies_browser_prompt": "Введите имя браузера (chrome, firefox, edge):",
                "tooltip_fragments": "Количество одновременно скачиваемых фрагментов.\nБольше = выше скорость, но сильнее нагрузка на процессор и сеть.",
                # значения качества для видео
                "quality_best": "Лучшее",
                "quality_2160p": "2160p (4K)",
                "quality_1440p": "1440p (2K)",
                "quality_1080p": "1080p",
                "quality_720p": "720p",
                # значения качества для аудио
                "quality_320": "320kbps",
                "quality_256": "256kbps",
                "quality_128": "128kbps",
                # Лог-сообщения
                "log_getting_info": "Получение информации...",
                "log_playlist_info": "Плейлист: {}, видео: {}",
                "log_video_info": "Название: {}, Длительность: {}, Размер: {} MB",
                "log_cookies_loaded": "Куки загружены из {}",
                "log_cookies_failed": "Не удалось извлечь куки. Авторизуйтесь в браузере и закройте его.",
                "log_cookies_error": "Ошибка: {}",
                "log_download_start": "Старт загрузки...",
                "log_download_progress": "Загрузка: {:.1f}% | Скорость: {} | Осталось: {}",
                "log_download_complete": "Скачивание завершено, постобработка...",
                "log_download_success": "Загрузка успешно завершена!",
                "log_download_cancel": "Загрузка отменена.",
                "log_download_error": "Ошибка: {}",
                "log_playlist_items": "Скачивание треков плейлиста: {}",
                "log_ffmpeg_path": "FFmpeg не найден. Убедитесь, что папка ffmpeg/bin существует.",
            },
            "en": {
                "url_label": "Video or playlist URL:",
                "info_btn": "Info",
                "login_btn": "Login to YouTube",
                "folder_btn": "Browse",
                "folder_path_label": "Path: {}",
                "audio_radio": "Audio",
                "video_radio": "Video",
                "quality_label": "Quality:",
                "fragments_label": "Fragments:",
                "audio_format_label": "Audio format:",
                "video_container_label": "Video container:",
                "playlist_range_label": "Playlist range (1-5 or 1,3,5):",
                "status_ready": "Ready",
                "status_cancel": "Canceling...",
                "status_processing": "Post-processing...",
                "status_completed": "Completed!",
                "status_error": "Error! Check the log",
                "download_btn": "START DOWNLOAD",
                "stop_btn": "STOP",
                "downloading_btn": "DOWNLOADING...",
                "update_btn": "Check for updates",
                "log_label": "Download log:",
                "no_url_title": "No URL",
                "no_url_msg": "Enter a video or playlist URL.",
                "already_downloading": "Download is already in progress.",
                "complete_title": "Complete",
                "complete_msg": "Files saved to:\n{}",
                "update_available_title": "Update Available",
                "update_available_msg": "New version of yt-dlp is available: {}\nYour version: {}\nOpen download page?",
                "update_error_title": "Update Check Failed",
                "update_error_msg": "Failed to check for updates: {}",
                "update_already": "yt-dlp is already up to date (version {})",
                "cookies_success_title": "Success",
                "cookies_success_msg": "Cookies loaded from {}.\nNow you can download age-restricted content.",
                "cookies_error_msg": "Could not load cookies from {}.\nMake sure the browser is closed.",
                "cookies_browser_prompt": "Enter browser name (chrome, firefox, edge):",
                "tooltip_fragments": "Number of fragments downloaded simultaneously.\nHigher = faster speed, but more CPU/network load.",
                "quality_best": "Best",
                "quality_2160p": "2160p (4K)",
                "quality_1440p": "1440p (2K)",
                "quality_1080p": "1080p",
                "quality_720p": "720p",
                "quality_320": "320kbps",
                "quality_256": "256kbps",
                "quality_128": "128kbps",
                # Лог-сообщения
                "log_getting_info": "Getting information...",
                "log_playlist_info": "Playlist: {}, videos: {}",
                "log_video_info": "Title: {}, Duration: {}, Size: {} MB",
                "log_cookies_loaded": "Cookies loaded from {}",
                "log_cookies_failed": "Failed to extract cookies. Log in to the browser and close it.",
                "log_cookies_error": "Error: {}",
                "log_download_start": "Starting download...",
                "log_download_progress": "Downloading: {:.1f}% | Speed: {} | ETA: {}",
                "log_download_complete": "Download completed, post-processing...",
                "log_download_success": "Download completed successfully!",
                "log_download_cancel": "Download canceled.",
                "log_download_error": "Error: {}",
                "log_playlist_items": "Downloading playlist tracks: {}",
                "log_ffmpeg_path": "FFmpeg not found. Make sure the ffmpeg/bin folder exists.",
            }
        }

    def set_language(self, lang_code):
        if lang_code in self._strings:
            self._current_lang = lang_code

    def get(self, key):
        return self._strings[self._current_lang].get(key, key)

    def get_quality_options(self, is_audio):
        if is_audio:
            return [self.get("quality_320"), self.get("quality_256"), self.get("quality_128")]
        else:
            return [self.get("quality_best"), self.get("quality_2160p"), self.get("quality_1440p"),
                    self.get("quality_1080p"), self.get("quality_720p")]

    def map_quality_value(self, localized_quality, is_audio):
        if is_audio:
            if localized_quality == self.get("quality_320"):
                return "320"
            elif localized_quality == self.get("quality_256"):
                return "256"
            elif localized_quality == self.get("quality_128"):
                return "128"
            else:
                return "320"
        else:
            if localized_quality == self.get("quality_best"):
                return "best"
            elif localized_quality == self.get("quality_2160p"):
                return "2160p"
            elif localized_quality == self.get("quality_1440p"):
                return "1440p"
            elif localized_quality == self.get("quality_1080p"):
                return "1080p"
            elif localized_quality == self.get("quality_720p"):
                return "720p"
            else:
                return "best"


class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Media Downloader | by Spaider")
        self.geometry("920x740")
        self.minsize(850, 740)

        self.cancel_download = False
        self.download_thread = None

        self.lang = LanguageManager()
        self.lang.set_language("en")  # Английский по умолчанию

        # FFmpeg
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.ffmpeg_dir = os.path.join(base_path, "ffmpeg", "bin")
        if not os.path.exists(self.ffmpeg_dir):
            print(self.lang.get("log_ffmpeg_path"))

        # Загрузка настроек
        self.settings = self.load_settings()
        self.username = getpass.getuser()
        default_path = self.settings.get("download_path", f"C:\\Users\\{self.username}\\Downloads")
        self.current_path = default_path

        self.create_widgets()
        self.apply_settings()
        self.url_entry.insert(0, self.settings.get("last_url", ""))

        self.last_update_time = 0
        self.last_percent = 0

    # ---------- JSON ----------
    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_settings(self):
        settings = {
            "download_path": self.current_path,
            "audio_quality": self.quality_var.get() if self.format_var.get() == "mp3" else None,
            "video_quality": self.quality_var.get() if self.format_var.get() == "mp4" else None,
            "concurrent_fragments": self.concurrent_var.get(),
            "last_format": self.format_var.get(),
            "last_container": self.container_var.get(),
            "last_audio_format": self.audio_format_var.get(),
            "last_url": self.url_entry.get(),
            "appearance_mode": ctk.get_appearance_mode(),
            "language": self.lang._current_lang
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)
        except:
            pass

    def apply_settings(self):
        # Загружаем сохранённый язык, если нет - английский
        saved_lang = self.settings.get("language", "en")
        if saved_lang in ["ru", "en"]:
            self.lang.set_language(saved_lang)

        # Синхронизируем переключатель языка (если он уже создан)
        if hasattr(self, 'language_switch'):
            if self.lang._current_lang == "ru":
                self.language_switch.set("Русский")
            else:
                self.language_switch.set("English")

        self.format_var.set(self.settings.get("last_format", "mp3"))
        self.update_quality_options(keep_value=True)
        self.container_var.set(self.settings.get("last_container", "mp4"))
        self.audio_format_var.set(self.settings.get("last_audio_format", "mp3"))

        saved_quality = None
        if self.format_var.get() == "mp3":
            saved_quality = self.settings.get("audio_quality")
        else:
            saved_quality = self.settings.get("video_quality")
        if saved_quality and saved_quality in self.quality_menu.cget("values"):
            self.quality_var.set(saved_quality)
        else:
            self.quality_var.set(self.quality_menu.cget("values")[0])

        fragments = self.settings.get("concurrent_fragments", 10)
        self.concurrent_var.set(fragments)
        self.fragments_slider.set(fragments)
        self.fragments_entry.delete(0, "end")
        self.fragments_entry.insert(0, str(fragments))

        ctk.set_appearance_mode(self.settings.get("appearance_mode", "dark"))
        self.update_ui_texts()

    # ---------- UI ----------
    def create_widgets(self):
        self.format_var = ctk.StringVar(value="mp3")
        self.quality_var = ctk.StringVar()
        self.concurrent_var = ctk.IntVar(value=10)
        self.audio_format_var = ctk.StringVar(value="mp3")
        self.container_var = ctk.StringVar(value="mp4")

        # Верхний фрейм
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(pady=10, padx=20, fill="x")

        self.url_label = ctk.CTkLabel(top_frame, text="", font=("Arial", 14))
        self.url_label.pack(anchor="w")
        url_frame = ctk.CTkFrame(top_frame)
        url_frame.pack(fill="x", pady=5)
        self.url_entry = ctk.CTkEntry(url_frame, placeholder_text="Вставьте ссылку здесь...")
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.info_btn = ctk.CTkButton(url_frame, width=60, command=self.get_info)
        self.info_btn.pack(side="right", padx=2)
        self.login_btn = ctk.CTkButton(url_frame, width=100, command=self.load_cookies_from_browser)
        self.login_btn.pack(side="right", padx=2)

        # Папка
        folder_frame = ctk.CTkFrame(top_frame)
        folder_frame.pack(fill="x", pady=5)
        self.folder_path_label = ctk.CTkLabel(folder_frame, text="", wraplength=500)
        self.folder_path_label.pack(side="left", padx=5)
        self.folder_btn = ctk.CTkButton(folder_frame, command=self.choose_path, width=80)
        self.folder_btn.pack(side="right", padx=5)

        # Основной фрейм настроек
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=10, padx=20, fill="x")

        # Строка 0: Аудио / Видео
        line0 = ctk.CTkFrame(self.settings_frame)
        line0.pack(fill="x", pady=5)

        self.audio_radio = ctk.CTkRadioButton(line0, variable=self.format_var, value="mp3", command=lambda: self.update_quality_options())
        self.audio_radio.pack(side="left", padx=(10, 5))
        self.audio_format_menu = ctk.CTkOptionMenu(line0, values=["mp3", "m4a", "ogg", "opus", "flac"],
                                                   variable=self.audio_format_var, width=100)
        self.audio_format_menu.pack(side="left", padx=(0, 20))

        self.video_radio = ctk.CTkRadioButton(line0, variable=self.format_var, value="mp4", command=lambda: self.update_quality_options())
        self.video_radio.pack(side="left", padx=(10, 5))
        self.container_menu = ctk.CTkOptionMenu(line0, values=["mp4", "webm", "mkv"],
                                                variable=self.container_var, width=100)
        self.container_menu.pack(side="left")

        # Строка 1: Качество + Фрагменты + Кнопка обновления
        line1 = ctk.CTkFrame(self.settings_frame)
        line1.pack(fill="x", pady=5)

        self.quality_label = ctk.CTkLabel(line1, text="")
        self.quality_label.pack(side="left", padx=(10, 5))
        self.quality_menu = ctk.CTkOptionMenu(line1, variable=self.quality_var, values=[], width=140)
        self.quality_menu.pack(side="left", padx=(0, 30))

        self.fragments_label = ctk.CTkLabel(line1, text="")
        self.fragments_label.pack(side="left", padx=(10, 5))
        self.fragments_slider = ctk.CTkSlider(line1, from_=1, to=20, number_of_steps=19,
                                              variable=self.concurrent_var, command=self.on_fragments_slider, width=150)
        self.fragments_slider.pack(side="left", padx=5)
        self.fragments_entry = ctk.CTkEntry(line1, width=50)
        self.fragments_entry.pack(side="left", padx=5)
        self.fragments_entry.bind("<KeyRelease>", self.on_fragments_entry)

        self.help_btn = ctk.CTkButton(line1, text="?", width=30, command=None, fg_color="gray", hover_color="dim gray")
        self.help_btn.pack(side="left", padx=(5, 0))
        # Подсказка с динамическим текстом (лямбда)
        ToolTip(self.help_btn, lambda: self.lang.get("tooltip_fragments"))

        self.update_btn = ctk.CTkButton(line1, command=self.check_for_ytdlp_update, width=150)
        self.update_btn.pack(side="right", padx=10)

        # Строка 2: Диапазон плейлиста
        playlist_frame = ctk.CTkFrame(self.settings_frame)
        playlist_frame.pack(fill="x", pady=5, padx=10)
        self.playlist_label = ctk.CTkLabel(playlist_frame, text="")
        self.playlist_label.pack(side="left", padx=(0, 10))
        self.playlist_range = ctk.CTkEntry(playlist_frame, width=200)
        self.playlist_range.pack(side="left")

        # Статус и прогресс
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 12), text_color="gray")
        self.status_label.pack(pady=(10, 0))
        self.progress_bar = ctk.CTkProgressBar(self, width=700)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)

        # Кнопки
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)
        self.download_button = ctk.CTkButton(button_frame, command=self.start_thread,
                                             height=50, font=("Arial", 16, "bold"), fg_color="#2b8a3e", width=250)
        self.download_button.pack(side="left", padx=10)
        self.stop_button = ctk.CTkButton(button_frame, command=self.cancel_downloading,
                                         height=50, font=("Arial", 16, "bold"), fg_color="#a83232", state="disabled", width=120)
        self.stop_button.pack(side="left", padx=10)

        # Лог
        log_frame = ctk.CTkFrame(self)
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.log_label = ctk.CTkLabel(log_frame, text="", anchor="w")
        self.log_label.pack(anchor="w", padx=(10, 0))
        self.log_textbox = ctk.CTkTextbox(log_frame, wrap="word")
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=5)

        # Переключатель языка
        self.language_switch = ctk.CTkSegmentedButton(self, values=["Русский", "English"],
                                                      command=self.change_language)
        self.language_switch.pack(pady=(5, 0))
        self.language_switch.set("Русский" if self.lang._current_lang == "ru" else "English")

        self.update_ui_texts()

    def update_ui_texts(self):
        self.url_label.configure(text=self.lang.get("url_label"))
        self.info_btn.configure(text=self.lang.get("info_btn"))
        self.login_btn.configure(text=self.lang.get("login_btn"))
        self.folder_btn.configure(text=self.lang.get("folder_btn"))
        self.update_folder_path_label()
        self.audio_radio.configure(text=self.lang.get("audio_radio"))
        self.video_radio.configure(text=self.lang.get("video_radio"))
        self.quality_label.configure(text=self.lang.get("quality_label"))
        self.fragments_label.configure(text=self.lang.get("fragments_label"))
        self.playlist_label.configure(text=self.lang.get("playlist_range_label"))
        self.update_btn.configure(text=self.lang.get("update_btn"))
        self.log_label.configure(text=self.lang.get("log_label"))
        self.download_button.configure(text=self.lang.get("download_btn"))
        if self.stop_button.cget("state") == "normal":
            self.stop_button.configure(text=self.lang.get("stop_btn"))
        else:
            self.stop_button.configure(text=self.lang.get("stop_btn"))  # просто установить текст
        if self.status_label.cget("text") in ("Готов к работе", "Ready"):
            self.status_label.configure(text=self.lang.get("status_ready"))
        self.update_quality_options(keep_value=True)

    def update_folder_path_label(self):
        self.folder_path_label.configure(text=self.lang.get("folder_path_label").format(self.current_path))

    def change_language(self, choice):
        new_lang = "ru" if choice == "Русский" else "en"
        self.lang.set_language(new_lang)
        self.update_ui_texts()
        self.save_settings()

    def update_quality_options(self, keep_value=False):
        is_audio = (self.format_var.get() == "mp3")
        new_options = self.lang.get_quality_options(is_audio)
        old_value = self.quality_var.get() if keep_value else None
        self.quality_menu.configure(values=new_options)
        if keep_value and old_value in new_options:
            self.quality_var.set(old_value)
        else:
            self.quality_var.set(new_options[0])
        if is_audio:
            self.audio_format_menu.configure(state="normal")
            self.container_menu.configure(state="disabled")
        else:
            self.audio_format_menu.configure(state="disabled")
            self.container_menu.configure(state="normal")

    def on_fragments_slider(self, value):
        self.concurrent_var.set(int(value))
        self.fragments_entry.delete(0, "end")
        self.fragments_entry.insert(0, str(int(value)))

    def on_fragments_entry(self, event):
        try:
            val = int(self.fragments_entry.get())
            val = max(1, min(20, val))
            self.concurrent_var.set(val)
            self.fragments_slider.set(val)
        except:
            pass

    def log(self, message_key, *args, **kwargs):
        """Выводит локализованное сообщение в лог и консоль"""
        text = self.lang.get(message_key)
        if args:
            text = text.format(*args)
        elif kwargs:
            text = text.format(**kwargs)
        timestamp = time.strftime("%H:%M:%S")
        self.log_textbox.insert("end", f"[{timestamp}] {text}\n")
        self.log_textbox.see("end")
        print(f"[{timestamp}] {text}")

    def cancel_downloading(self):
        self.cancel_download = True
        self.log("status_cancel")
        self.status_label.configure(text=self.lang.get("status_cancel"), text_color="orange")

    def choose_path(self):
        path = filedialog.askdirectory()
        if path:
            self.current_path = path
            self.update_folder_path_label()
            self.save_settings()

    def get_quality_value(self):
        localized = self.quality_var.get()
        is_audio = (self.format_var.get() == "mp3")
        return self.lang.map_quality_value(localized, is_audio)

    def get_info(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning(self.lang.get("no_url_title"), self.lang.get("no_url_msg"))
            return
        self.log("log_getting_info")
        try:
            ydl_opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    title = info.get('title', 'N/A')
                    count = len(info['entries'])
                    self.log("log_playlist_info", title, count)
                else:
                    title = info.get('title', 'N/A')
                    duration = info.get('duration', 0)
                    size = info.get('filesize', 0) or info.get('filesize_approx', 0)
                    size_mb = f"{size/1024/1024:.1f}" if size else "?"
                    self.log("log_video_info", title, f"{duration//60}:{duration%60:02d}", size_mb)
                    messagebox.showinfo(self.lang.get("info_btn"),
                                        f"Название: {title}\nДлительность: {duration//60}:{duration%60:02d}\nРазмер: {size_mb} MB")
        except Exception as e:
            self.log("log_download_error", str(e))

    def load_cookies_from_browser(self):
        browsers = ["chrome", "firefox", "edge", "opera", "brave"]
        dialog = ctk.CTkInputDialog(text=self.lang.get("cookies_browser_prompt"), title="Cookies")
        b = dialog.get_input()
        if not b:
            return
        b = b.lower()
        if b in browsers:
            try:
                ck = yt_dlp.cookies.extract_cookies_from_browser(b, None)
                if ck:
                    self.log("log_cookies_loaded", b)
                    messagebox.showinfo(self.lang.get("cookies_success_title"),
                                        self.lang.get("cookies_success_msg").format(b))
                else:
                    self.log("log_cookies_failed")
            except Exception as e:
                self.log("log_cookies_error", str(e))
                messagebox.showerror(self.lang.get("cookies_success_title"),
                                     self.lang.get("cookies_error_msg").format(b))
        else:
            messagebox.showwarning("Ошибка", "Введите корректное имя: chrome, firefox, edge, opera, brave")

    def check_for_ytdlp_update(self):
        def check():
            try:
                response = requests.get("https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest")
                response.raise_for_status()
                latest_version = response.json()["tag_name"].lstrip('v')
                try:
                    current_version = yt_dlp.version.__version__
                except Exception:
                    result = subprocess.run([sys.executable, "-m", "yt_dlp", "--version"],
                                            capture_output=True, text=True, check=False)
                    current_version = result.stdout.strip() if result.returncode == 0 else "unknown"
                if current_version != "unknown" and version.parse(current_version) < version.parse(latest_version):
                    self.after(0, lambda: self.prompt_update(latest_version, current_version))
                else:
                    msg = self.lang.get("update_already").format(current_version if current_version != "unknown" else "?")
                    self.after(0, lambda: messagebox.showinfo(self.lang.get("update_available_title"), msg))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(self.lang.get("update_error_title"),
                                                           self.lang.get("update_error_msg").format(str(e))))
        threading.Thread(target=check, daemon=True).start()

    def prompt_update(self, latest, current):
        if messagebox.askyesno(self.lang.get("update_available_title"),
                               self.lang.get("update_available_msg").format(latest, current)):
            webbrowser.open("https://github.com/yt-dlp/yt-dlp/releases/latest")

    def progress_hook(self, d):
        if self.cancel_download:
            raise Exception("Отмена")
        if d['status'] == 'downloading':
            try:
                p = float(d.get('_percent_str', '0%').replace('%', ''))
                now = time.time()
                if now - self.last_update_time > 0.2 or abs(p - self.last_percent) >= 0.5:
                    self.last_update_time = now
                    self.last_percent = p
                    self.progress_bar.set(p / 100)
                    speed = d.get('_speed_str', 'N/A')
                    eta = d.get('_eta_str', 'N/A')
                    total = d.get('_total_bytes_str', d.get('_total_bytes_estimate_str', 'N/A'))
                    self.status_label.configure(text=f"Скорость: {speed} | Осталось: {eta} | Размер: {total}",
                                                text_color="white")
                    self.log("log_download_progress", p, speed, eta)
            except:
                pass
        elif d['status'] == 'finished':
            self.status_label.configure(text=self.lang.get("status_processing"), text_color="#f0ad4e")
            self.log("log_download_complete")

    def start_thread(self):
        if self.download_thread and self.download_thread.is_alive():
            messagebox.showwarning(self.lang.get("already_downloading"), self.lang.get("already_downloading"))
            return
        self.cancel_download = False
        self.download_button.configure(state="disabled", text=self.lang.get("downloading_btn"))
        self.stop_button.configure(state="normal", text=self.lang.get("stop_btn"))
        self.progress_bar.set(0)
        self.log("log_download_start")
        self.download_thread = threading.Thread(target=self.start_download, daemon=True)
        self.download_thread.start()

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            self.after(0, lambda: messagebox.showwarning(self.lang.get("no_url_title"), self.lang.get("no_url_msg")))
            self.reset_ui()
            return

        fmt = self.format_var.get()
        quality_value = self.get_quality_value()
        container = self.container_var.get() if fmt == "mp4" else "mp3"
        concurrent = self.concurrent_var.get()

        playlist_range = self.playlist_range.get().strip()
        playlist_items = None
        if playlist_range:
            items = []
            for part in playlist_range.split(','):
                part = part.strip()
                if '-' in part:
                    try:
                        a, b = map(int, part.split('-'))
                        items.extend(range(a, b+1))
                    except:
                        pass
                else:
                    try:
                        items.append(int(part))
                    except:
                        pass
            if items:
                playlist_items = items
                self.log("log_playlist_items", str(playlist_items))

        ydl_opts = {
            'outtmpl': f'{self.current_path}/%(title)s.%(ext)s',
            'ffmpeg_location': self.ffmpeg_dir,
            'ignoreerrors': True,
            'writethumbnail': True,
            'progress_hooks': [self.progress_hook],
            'concurrent_fragment_downloads': concurrent,
            'external_downloader_args': ['-j', '16'],
            'writemetadata': True,
            'parse_metadata': 'playlist_index:%(track_number)s',
            'playlist_items': ','.join(map(str, playlist_items)) if playlist_items else None,
        }

        if fmt == "mp3":
            audio_codec = self.audio_format_var.get()
            codec_map = {"mp3": "mp3", "m4a": "aac", "ogg": "vorbis", "opus": "opus", "flac": "flac"}
            codec = codec_map.get(audio_codec, "mp3")
            ext = audio_codec if audio_codec != "m4a" else "m4a"
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [
                    {'key': 'FFmpegExtractAudio', 'preferredcodec': codec,
                     'preferredquality': quality_value},
                    {'key': 'EmbedThumbnail'},
                    {'key': 'FFmpegMetadata', 'add_chapters': True, 'add_metadata': True},
                ],
                'outtmpl': f'{self.current_path}/%(title)s.{ext}',
            })
        else:
            if quality_value == "best":
                format_str = f'bestvideo[ext={container}]+bestaudio/best[ext={container}]'
            else:
                height = quality_value.replace('p', '')
                format_str = f'bestvideo[height<={height}][ext={container}]+bestaudio/best[height<={height}][ext={container}]'
            ydl_opts.update({
                'format': format_str,
                'merge_output_format': container,
                'postprocessors': [{'key': 'FFmpegMetadata', 'add_chapters': True, 'add_metadata': True}],
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            if not self.cancel_download:
                self.log("log_download_success")
                self.status_label.configure(text=self.lang.get("status_completed"), text_color="#2b8a3e")
                messagebox.showinfo(self.lang.get("complete_title"), self.lang.get("complete_msg").format(self.current_path))
        except Exception as e:
            if self.cancel_download:
                self.log("log_download_cancel")
            else:
                self.log("log_download_error", str(e))
                traceback.print_exc()
                self.status_label.configure(text=self.lang.get("status_error"), text_color="red")
        finally:
            self.reset_ui()
            self.save_settings()

    def reset_ui(self):
        self.download_button.configure(state="normal", text=self.lang.get("download_btn"))
        self.stop_button.configure(state="disabled", text=self.lang.get("stop_btn"))
        self.progress_bar.set(0)
        self.cancel_download = False
        self.download_thread = None
        self.last_update_time = 0
        self.last_percent = 0


if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()