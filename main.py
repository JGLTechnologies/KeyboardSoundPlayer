import asyncio
import json
import shutil
import tkinter
from concurrent.futures import ThreadPoolExecutor
import time
import pygame
import pyttsx3
from pynput import keyboard
from pytube import YouTube
import requests
from moviepy.video.io.VideoFileClip import AudioFileClip
import os
from aiohttp.web import Application, RouteTableDef, Request, Response, run_app
import filelock
from tkinter import *
from tkinter import ttk
import sys

if sys.platform.startswith("win"):
    lock = filelock.WindowsFileLock(lock_file="lock", timeout=1)
else:
    lock = filelock.UnixFileLock(lock_file="lock", timeout=1)


def disable_event():
    pass


try:
    with lock.acquire():
        root: tkinter.Tk
        done = False
        progress: ttk.Progressbar
        last_exit_press = time.time()
        exit_presses = 1
        all_ = False
        last_reset = time.time()
        enabled = True
        aiohttp_pool = ThreadPoolExecutor(1)
        app = Application()
        shutdown = False
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
            gender = 0
            rate = 150
            channels = 8
            yt_update = False
            exit_key = "esc"
            port = 6238

        try:
            with open("keys.json") as f:
                keys = json.load(f)
        except Exception:
            keys = {}


        def start_pb():
            global root, progress
            root = Tk()
            progress = ttk.Progressbar(root, orient=HORIZONTAL, length=100, mode="determinate")
            root.protocol("WM_DELETE_WINDOW", disable_event)
            root.title("KeyboardSoundPlayer")
            root.resizable(False, False)
            root.geometry("250x75")
            progress.pack(pady=20)
            root.attributes('-topmost', 1)

            def loop():
                if done:
                    root.destroy()
                else:
                    root.after(100, loop)

            root.after(100, loop)
            root.mainloop()


        def connected() -> bool:
            try:
                with requests.Session() as session:
                    with session.get("http://google.com", timeout=5):
                        pass
            except Exception:
                return False
            return True


        def save_to_file():
            global all_
            global progress
            global root
            global done
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
                    vid = YouTube(url=keys[key])
                    if os.path.exists(f"{key}.mp3") and not yt_update:
                        progress["value"] += float(100) / (len(keys) + 1)
                        continue
                    name = vid.streams.filter(file_extension="mp4").first().download()
                    video = AudioFileClip(name)
                    video.write_audiofile(f"{key}.mp3")
                    video.close()
                    os.remove(name)
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


        with ThreadPoolExecutor(1) as pool:
            def stop():
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


            def on_press(key_):
                global enabled
                global exit_presses
                global last_exit_press
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
                        stop()
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


            listener = keyboard.Listener(on_press=on_press)
            pool.submit(start_pb)
            save_to_file()
            pool.submit(pygame.init)
            pool.submit(pygame.mixer.set_num_channels, channels)
            routes = RouteTableDef()


            @routes.get("/online")
            async def online(request: Request):
                return Response(text="True", status=200)


            @routes.get("/stop")
            async def online(request: Request):
                stop()
                return Response(text="ok", status=200)


            @routes.get("/play")
            async def play_endpoint(request: Request):
                global enabled
                global exit_presses
                global last_exit_press
                if all_:
                    try:
                        if enabled:
                            pool.submit(play, "all.mp3")
                    except Exception:
                        pass
                k = request.query["key"]
                if k == exit_key:
                    if last_exit_press + 2 <= time.time():
                        exit_presses = 1
                    if exit_presses >= 5:
                        stop()
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


            async def loop():
                while True:
                    if shutdown:
                        await app.shutdown()
                        await app.cleanup()
                        sys.exit()
                    await asyncio.sleep(.5)


            async def startup(app: Application):
                asyncio.get_event_loop().create_task(loop())


            def run_server():
                run_app(app, port=port)


            app.on_startup.append(startup)
            app.add_routes(routes)
            aiohttp_pool.submit(run_server)
            listener.run()

except filelock.Timeout:
    sys.exit()
