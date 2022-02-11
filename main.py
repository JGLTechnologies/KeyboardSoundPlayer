import json
import sys
import threading
import time
import pygame
import pyttsx3
from pynput import keyboard

esc_presses = 1
all_ = False


def clear_presses():
    global esc_presses
    time.sleep(2)
    esc_presses = 1


def on_press(key_):
    global esc_presses
    if all_:
        try:
            pygame.mixer.Sound(f"all.mp3").play()
        except Exception:
            pass
    try:
        k = key_.name
        if k == "esc" and esc_presses >= 5:
            pygame.quit()
            sys.exit()
        elif k == "esc":
            if esc_presses == 1:
                threading.Thread(target=clear_presses).start()
            esc_presses += 1
    except AttributeError:
        k = key_.char
    if k in keys:
        if keys[k] == "reset()":
            pygame.quit()
            pygame.init()
    try:
        pygame.mixer.Sound(f"{k}.mp3").play()
    except Exception:
        return


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
except FileNotFoundError:
    gender = 0
    rate = 150

try:
    with open("keys.json") as f:
        keys = json.load(f)
except FileNotFoundError:
    keys = {}


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
        if keys[key].endswith("()"):
            continue
        engine.save_to_file(keys[key], f"{key}.mp3")
    engine.runAndWait()


listener = keyboard.Listener(on_press=on_press)
save_to_file()
pygame.init()
listener.run()
