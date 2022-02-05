import json
import sys
import pygame
import pyttsx3
from pynput import keyboard


def on_press(key_):
    try:
        if key_.name == "esc":
            pygame.quit()
            sys.exit()
        k = key_.name
    except AttributeError:
        k = key_.char
    for key in keys:
        if k == key:
            pygame.mixer.Sound(f"{key}.mp3").play()


try:
    with open("config.json", "r") as f:
        data = json.load(f)
        gender = data.get("gender") or "male"
        rate = data.get("rate") or 150
        if gender.lower() == "male":
            gender = 0
        elif gender.lower() == "female":
            gender = 1
        else:
            gender = 0
except FileNotFoundError:
    gender = 0
    rate = 150

with open("keys.json") as f:
    keys = json.load(f)


def save_to_file():
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[gender].id)
    for key in keys:
        engine.save_to_file(keys[key], f"{key}.mp3")
    engine.runAndWait()


listener = keyboard.Listener(on_press=on_press)
save_to_file()
pygame.init()
listener.run()
