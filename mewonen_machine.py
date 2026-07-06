import os
import random
import requests
from datetime import datetime
from moviepy import *
import numpy as np

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("MEWONEN_VOICE_ID", "")
PIXABAY_KEY = os.environ.get("PIXABAY_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")

SCRIPT_TEMPLATES = [
    {"hook": "checked my bank account", "body": ["I looked at the number. It looked back at me.", "My balance and motivation are both low.", "The ATM asked for a receipt. I declined."], "punchline": "Money comes and goes. Mostly goes."},
    {"hook": "tried to make friends", "body": ["I smiled. They stared at their phone.", "200 messages. None for me.", "Adulthood is sending memes. Hoping."], "punchline": "Maybe tomorrow. Or not."},
    {"hook": "read the news", "body": ["Bad news. More bad news. A dog. The dog was fine.", "I scrolled 40 minutes. 47 new worries.", "The world burns. New chips flavor."], "punchline": "I closed the app. The world waited."},
    {"hook": "went outside", "body": ["Too hot. Phone overheated. I overheated.", "A bird judged me.", "Nature is beautiful. And dangerous."], "punchline": "Back inside. AC is my friend."},
    {"hook": "tried to sleep", "body": ["2am. Mistakes since 2018. Replay.", "3am. Solved hunger. Forgot.", "4am. Penguins. Cried."], "punchline": "Alarm at 7. Aged 10 years."},
    {"hook": "used a dating app", "body": ["50 swipes. One match. Selling crypto.", "Hobby: surviving. Unmatched.", "Love is sharing Netflix."], "punchline": "Adopting another plant."},
    {"hook": "called my mom", "body": ["Eating dry cereal. She asked if I eat well.", "Love life? My plant is thriving.", "She's proud. I needed that."], "punchline": "Moms know everything."},
    {"hook": "went to work", "body": ["3 meetings. 2 could be emails. 1 a text.", "We're family. Families don't fire on Zoom.", "8 hours. Screen stared back."], "punchline": "I work to afford work."},
    {"hook": "tried to be healthy", "body": ["Salad costs more than Netflix.", "I ran. Lungs questioned me.", "Water. Pure. Boring. I miss soda."], "punchline": "Temple. Wants pizza."},
    {"hook": "checked social media", "body": ["Everyone is winning. I'm eating toast.", "Posted. 3 likes. Mom. Bot. Accident.", "Comparison is the thief of joy."], "punchline": "Toast was cold. Life goes on."}
]

HASHTAGS = "#mewonen #relatable #humor #life #mood #viral #fyp"

def send_message(text):
    try: requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
    except: pass

def send_video(path, caption):
    try:
        with open(path, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"video": f}, timeout=60)
        return True
    except: return False

def gen_script():
    t = random.choice(SCRIPT_TEMPLATES)
    b = random.choice(t["body"])
    return f"Mewonen. Somewhere in the world.\n\nToday I {t['hook']}.\n\n{b}\n\n{t['punchline']}\n\nSee you tomorrow. Maybe."

def gen_voice(script):
    try:
        r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}", headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}, json={"text": script, "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}, timeout=30)
        if r.status_code == 200:
            p = "/tmp/audio.mp3"
            with open(p, "wb") as f: f.write(r.content)
            return p
    except: pass
    return None

def get_bg():
    q = random.choice(["city night", "sunset sky", "rain window", "quiet morning", "clouds", "empty street", "coffee shop"])
    try:
        r = requests.get(f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q={q}&per_page=5&orientation=vertical", timeout=10)
        hits = r.json().get("hits", [])
        if not hits: return None
        v = random.choice(hits).get("videos", {})
        for s in ["large", "medium", "small", "tiny"]:
            if s in v:
                r2 = requests.get(v[s]["url"], timeout=30)
                p = "/tmp/bg.mp4"
                with open(p, "wb") as f: f.write(r2.content)
                return p
    except: pass
    return None

def make_video(audio_path, bg_path, script):
    try:
        audio = AudioFileClip(audio_path)
        dur = audio.duration + 1
        if bg_path:
            bg = VideoFileClip(bg_path)
            bg = bg.loop(duration=dur) if bg.duration < dur else bg.subclip(0, dur)
            bg = bg.resize(height=1920)
            if bg.w > 1080: bg = bg.crop(x_center=bg.w/2, width=1080)
            if bg.w < 1080: bg = bg.resize(width=1080)
        else:
            bg = ColorClip(size=(1080, 1920), color=(10, 10, 24), duration=dur)
        bg = bg.set_audio(audio)
        wm1 = TextClip("© Mewonen", fontsize=35, color='white', stroke_color='black', stroke_width=1).set_opacity(0.5).set_position(('center', 0.88), relative=True).set_duration(dur)
        wm2 = TextClip("mewonen.com", fontsize=28, color='white', stroke_color='black', stroke_width=1).set_opacity(0.4).set_position(('center', 0.94), relative=True).set_duration(dur)
        final = CompositeVideoClip([bg, wm1, wm2])
        out = "/tmp/video.mp4"
        final.write_videofile(out, codec='libx264', audio_codec='aac', fps=24, preset='ultrafast', threads=2, logger=None)
        bg.close(); final.close(); audio.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        return None

def main():
    send_message("🎬 Mewonen Engine — Starting...")
    script = gen_script()
    audio = gen_voice(script)
    if not audio: send_message("❌ Voice failed"); return
    bg = get_bg()
    video = make_video(audio, bg, script)
    if not video: send_message("❌ Video failed"); return
    caption = f"{script.split(chr(10))[2]}\n\n💜 mewonnen.com\n\n{HASHTAGS}"
    ok = send_video(video, caption)
    if ok: send_message(f"✅ Posted!\n\n📝 {script[:150]}...")
    else: send_message("❌ Post failed")

if __name__ == "__main__":
    main()
