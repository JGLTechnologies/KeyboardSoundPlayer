import json
from concurrent.futures import ThreadPoolExecutor
import time
import sys
import pygame
import pyttsx3
from pynput import keyboard
from pytube import YouTube
import requests
from moviepy.video.io.VideoFileClip import VideoFileClip
import os

last_esc = time.time()
esc_presses = 1
all_ = False
last_reset = time.time()

try:
    with open("config.json", "r") as f:
        data = json.load(f)
        gender = data.get("gender") or "male"
        rate = data.get("rate") or 170
        if gender.lower() == "male":
            gender = 0
        elif gender.lower() == "female":
            gender = 1
        else:
            gender = 0
        channels = data.get("channels") or 8
except FileNotFoundError:
    gender = 0
    rate = 150

try:
    with open("keys.json") as f:
        keys = json.load(f)
except FileNotFoundError:
    keys = {}


def connected() -> bool:
    try:
        with requests.Session() as session:
            with session.get("http://google.com", timeout=5):
                pass
    except Exception:
        return False
    return True


with ThreadPoolExecutor(1) as pool:
    def play(file: str):
        try:
            pygame.mixer.Sound(file).play()
        except Exception:
            return


    def reset():
        global last_reset
        pygame.mixer.stop()
        last_reset = time.time()


    def on_press(key_):
        global esc_presses
        global last_esc
        if all_:
            try:
                pool.submit(play, "all.mp3")
            except Exception:
                pass
        try:
            k = key_.name
            if k == "esc":
                if last_esc + 2 <= time.time():
                    esc_presses = 1
                if esc_presses >= 5:
                    pool.submit(pygame.quit)
                    sys.exit()
                elif esc_presses == 1:
                    last_esc = time.time()
                esc_presses += 1
        except AttributeError:
            k = key_.char
        if k in keys:
            if keys[k] == "reset()":
                if last_reset + 1 <= time.time():
                    pool.submit(reset)
                else:
                    return
        try:
            pool.submit(play, f"{k}.mp3")
        except Exception:
            return


    def save_to_file():
        global all_
        try:
            with open("all.mp3"):
                pass
            all_ = True
        except FileNotFoundError:
            pass
        engine = pyttsx3.init()
        engine.setProperty("rate", rate)
        voices = engine.getProperty("voices")
        engine.setProperty("voice", voices[gender].id)
        for key in keys:
            if keys[key].startswith("https://") and connected():
                vid = YouTube(url=keys[key])
                name = vid.streams.filter(file_extension="mp4").first().download()
                video = VideoFileClip(name.split("\\")[-1])
                video.audio.write_audiofile(f"{key}.mp3")
                video.close()
                os.remove(name)
                continue
            if keys[key].endswith("()"):
                continue
            engine.save_to_file(keys[key], f"{key}.mp3")
        engine.runAndWait()


    listener = keyboard.Listener(on_press=on_press)
    save_to_file()
    pool.submit(pygame.init)
    pool.submit(pygame.mixer.set_num_channels, channels)
    listener.run()
