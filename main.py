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
from aiohttp.web import Application, RouteTableDef, Request, Response, run_app
from disnake.ext import tasks
import filelock

lock = filelock.WindowsFileLock(lock_file="lock", timeout=1)
try:
    with lock.acquire():
        last_exit_press = time.time()
        exit_presses = 1
        all_ = False
        last_reset = time.time()
        enabled = True
        aiohttp_pool = ThreadPoolExecutor(1)
        app = Application()
        shutdown = False
        mp3s = {}

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
        except FileNotFoundError:
            gender = 0
            rate = 150
            channels = 8
            yt_update = False
            exit_key = "esc"
            port = 6238

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
                if keys[key] == "all":
                    all_ = True
                if keys[key].startswith("https://"):
                    if not connected():
                        continue
                    vid = YouTube(url=keys[key])
                    if os.path.exists(f"{key}.mp3") and not yt_update:
                        continue
                    name = vid.streams.filter(file_extension="mp4").first().download()
                    video = VideoFileClip(name)
                    video.audio.write_audiofile(f"{key}.mp3")
                    video.close()
                    os.remove(name)
                    continue
                if keys[key].endswith("()"):
                    continue
                if keys[key].endswith(".mp3"):
                    mp3s[key] = keys[key]
                    continue
                engine.save_to_file(keys[key], f"{key}.mp3")
            engine.runAndWait()


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
                    if k == exit_key:
                        if last_exit_press + 2 <= time.time():
                            exit_presses = 1
                        if exit_presses >= 5:
                            stop()
                        elif exit_presses == 1:
                            last_exit_press = time.time()
                        exit_presses += 1
                except AttributeError:
                    k = key_.char
                if k in keys:
                    if keys[k] == "reset()":
                        if last_reset + 1 <= time.time():
                            pool.submit(reset)
                        else:
                            return
                    elif keys[k] == "toggle()":
                        enabled = not enabled
                        return
                try:
                    if enabled:
                        if k in mp3s:
                            file = mp3s[k]
                        else:
                            file = f"{k}.mp3"
                        pool.submit(play, file)
                except Exception:
                    return


            listener = keyboard.Listener(on_press=on_press)
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


            @tasks.loop(seconds=.5)
            async def shutdown_loop():
                if shutdown:
                    await app.shutdown()
                    await app.cleanup()
                    sys.exit()


            async def startup(app: Application):
                shutdown_loop.start()


            def run_server():
                run_app(app, port=port)


            app.on_startup.append(startup)
            app.add_routes(routes)
            aiohttp_pool.submit(run_server)
            listener.run()
except filelock.Timeout:
    sys.exit()
