import asyncio
import functools
import json
import shutil
import tkinter
from tkinter import messagebox
from concurrent.futures import ThreadPoolExecutor
import time
import pygame
import pyttsx3
from pynput import keyboard
import requests
import os
from aiohttp.web import Application, RouteTableDef, Request, Response, run_app
import filelock
from tkinter import *
import sys
from yt_dlp import YoutubeDL
from tkinter import ttk

# Setup
done = False
last_exit_press = time.time()
exit_presses = 1
all_ = False
last_reset = time.time()
enabled = True
app = Application()
shutdown = False
progress: ttk.Progressbar
routes = RouteTableDef()

# Config
gender = 0
rate = 150
channels = 8
yt_update = False
exit_key = "esc"
port = 6238
keys = {}

if sys.platform.startswith("win"):
    lock = filelock.WindowsFileLock(lock_file="lock", timeout=1)
else:
    lock = filelock.UnixFileLock(lock_file="lock", timeout=1)


def disable_event():
    pass


def show_error_popup(message):
    r = tkinter.Tk()
    r.withdraw()  # Hide the root window
    messagebox.showerror("Error", message)  # Show the error popup
    r.destroy()  # Close the root window after the popup


def download_audio_as_mp3(key, url):
    options = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }
        ],
        "outtmpl": f"{key}",
        "quiet": True,
    }

    with YoutubeDL(options) as ydl:
        ydl.download([url])


def connected() -> bool:
    try:
        with requests.Session() as session:
            with session.get("http://google.com", timeout=5):
                pass
    except Exception:
        return False
    return True


def setup():
    global gender, rate, channels, yt_update, exit_key, port, keys
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
            yt_update = data.get("yt_update") or False
            exit_key = data.get("exit_key") or "esc"
            port = data.get("port") or 6238
    except Exception:
        pass
    try:
        with open("keys.json") as f:
            keys = json.load(f)
    except Exception:
        return


def start_pb():
    global progress
    root = Tk()
    progress = ttk.Progressbar(root, orient=HORIZONTAL, length=100, mode="determinate")
    root.protocol("WM_DELETE_WINDOW", disable_event)
    root.title("KeyboardSoundPlayer")
    root.resizable(False, False)
    root.geometry("250x75")
    progress.pack(pady=20)
    root.attributes("-topmost", 1)

    def pb_loop():
        if done:
            root.destroy()
        else:
            root.after(100, pb_loop)

    root.after(100, pb_loop)
    root.mainloop()
    return progress


def save_to_file():
    global all_, done, progress
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
        if key == "all":
            all_ = True
        if keys[key].startswith("https://"):
            if not connected():
                progress["value"] += float(100) / (len(keys) + 1)
                continue
            if os.path.exists(f"{key}.mp3") and not yt_update:
                progress["value"] += float(100) / (len(keys) + 1)
                continue
            try:
                download_audio_as_mp3(key, keys[key])
            except Exception as e:
                show_error_popup(
                    f"Error downloading audio for key: {key}\nContact us at jgltechnologies.com/contact"
                )
                continue
            progress["value"] += float(100) / (len(keys) + 1)
            continue
        if keys[key].endswith("()"):
            progress["value"] += float(100) / (len(keys) + 1)
            continue
        if keys[key].endswith(".mp3"):
            shutil.copyfile(keys[key], f"{key}.mp3")
            progress["value"] += float(100) / (len(keys) + 1)
            continue
        engine.save_to_file(keys[key], f"{key}.mp3")
        progress["value"] += float(100) / (len(keys) + 1)
    engine.runAndWait()
    progress["value"] += float(100) / (len(keys) + 1)
    time.sleep(1)
    done = True


def quit_app(pool: ThreadPoolExecutor):
    global shutdown
    shutdown = True
    pool.submit(pygame.quit)
    os._exit(1)


def play(file: str):
    try:
        pygame.mixer.Sound(file).play()
    except Exception:
        return


def reset():
    global last_reset
    pygame.mixer.stop()
    last_reset = time.time()


def on_press(pool: ThreadPoolExecutor, key_):
    global enabled, exit_presses, last_exit_press
    if all_:
        try:
            if enabled:
                pool.submit(play, "all.mp3")
        except Exception:
            pass
    try:
        k = key_.name
    except AttributeError:
        k = key_.char
    if k == exit_key:
        if last_exit_press + 2 <= time.time():
            exit_presses = 1
        if exit_presses >= 5:
            quit_app(app.pool)
        elif exit_presses == 1:
            last_exit_press = time.time()
        exit_presses += 1

    if k in keys:
        if keys[k] == "reset()":
            if enabled:
                if last_reset + 1 <= time.time():
                    pool.submit(reset)
                else:
                    return
        elif keys[k] == "toggle()":
            enabled = not enabled
            return
        elif keys[k] == "pause()":
            if enabled:
                pool.submit(pygame.mixer.pause)
        elif keys[k] == "unpause()":
            if enabled:
                pool.submit(pygame.mixer.unpause)
    try:
        if enabled:
            file = f"{k}.mp3"
            pool.submit(play, file)
    except Exception:
        return


@routes.get("/online")
async def online_endpoint(request: Request):
    return Response(text="True", status=200)


@routes.get("/stop")
async def stop_endpoint(request: Request):
    quit_app(app.pool)
    return Response(text="ok", status=200)


@routes.get("/play")
async def play_endpoint(request: Request):
    global enabled, exit_presses, last_exit_press
    if all_:
        try:
            if enabled:
                app.pool.submit(play, "all.mp3")
        except Exception:
            pass
    k = request.query.get("key")
    if k is None:
        return Response(text="Key is required", status=400)
    k = k[0].lower()
    if k not in keys:
        print(keys)
        return Response(text="Key is invalid", status=400)
    if k == exit_key:
        if last_exit_press + 2 <= time.time():
            exit_presses = 1
        if exit_presses >= 5:
            quit_app(app.pool)
        elif exit_presses == 1:
            last_exit_press = time.time()
        exit_presses += 1

    if k in keys:
        if keys[k] == "reset()":
            if enabled:
                if last_reset + 1 <= time.time():
                    app.pool.submit(reset)
                    return Response(text="ok", status=200)
                else:
                    return Response(text="ok", status=200)
        elif keys[k] == "toggle()":
            enabled = not enabled
            return Response(text="ok", status=200)
        elif keys[k] == "pause()":
            if enabled:
                app.pool.submit(pygame.mixer.pause)
                return Response(text="ok", status=200)
        elif keys[k] == "unpause()":
            if enabled:
                app.pool.submit(pygame.mixer.unpause)
                return Response(text="ok", status=200)
    try:
        if enabled:
            file = f"{k}.mp3"
            app.pool.submit(play, file)
            return Response(text="ok", status=200)
    except Exception as e:
        return Response(text=str(e), status=500)


async def loop():
    while True:
        if shutdown:
            await app.shutdown()
            await app.cleanup()
            sys.exit()
        await asyncio.sleep(0.5)


async def startup(app: Application):
    asyncio.get_event_loop().create_task(loop())


def run_server(pool: ThreadPoolExecutor):
    app.pool = pool
    run_app(app, port=port)


def main():
    setup()
    with ThreadPoolExecutor(1) as pool:
        aiohttp_pool = ThreadPoolExecutor(1)
        app.on_startup.append(startup)
        app.add_routes(routes)
        aiohttp_pool.submit(run_server, pool)
        listener = keyboard.Listener(on_press=functools.partial(on_press, pool))
        pool.submit(save_to_file)
        start_pb()
        pool.submit(pygame.init)
        pool.submit(pygame.mixer.set_num_channels, channels)
        listener.run()


try:
    with lock.acquire():
        if __name__ == "__main__":
            main()
except filelock.Timeout:
    sys.exit()
