import os
import random
import requests
from datetime import datetime
from moviepy.editor import *
import numpy as np

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("MEWONEN_VOICE_ID", "")
PIXABAY_KEY = os.environ.get("PIXABAY_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")

SCRIPT_TEMPLATES = [
    {"hook": "checked my bank account", "body": ["I looked at the number. It looked back at me. Neither of us was happy.", "My balance and my motivation have something in common. They're both low.", "The ATM asked if I wanted a receipt. I said no. I didn't need proof."], "punchline": "Money comes and goes. Mostly goes."},
    {"hook": "tried to make friends today", "body": ["I smiled at someone in the elevator. They stared at their phone harder.", "I joined a group chat. 200 messages. Not one was for me.", "Being an adult is just sending memes and hoping someone replies."], "punchline": "Maybe tomorrow. Or maybe I'll just stay home."},
    {"hook": "read the news today", "body": ["Bad news. More bad news. A cute dog. Catastrophe. The dog was fine.", "I scrolled for 40 minutes. I know 47 things to worry about now.", "The world is on fire but there's a new flavor of chips."], "punchline": "I closed the app. The world was still there. Waiting."},
    {"hook": "went outside today", "body": ["It's too hot. My phone overheated. I overheated. The pavement is cooking.", "A bird looked at me. I think it was judging my life choices.", "Nature is beautiful. Nature is also trying to end us with heat."], "punchline": "I went back inside. The AC is my only friend."},
    {"hook": "tried to sleep last night", "body": ["2am. My brain replayed every mistake since 2018.", "3am. I solved world hunger. Forgot it by morning.", "4am. Watched penguins. Cried. Not because of the penguins."], "punchline": "Alarm at 7. I aged 10 years overnight."},
    {"hook": "used a dating app", "body": ["Swiped right 50 times. One match. They were selling crypto.", "Someone asked my hobbies. I said surviving. They unmatched.", "Love in 2026 is sharing a Netflix account."], "punchline": "Maybe I'll adopt another plant."},
    {"hook": "called my mom", "body": ["She asked if I'm eating well. I was eating dry cereal.", "She asked about love. I told her my plant is doing great.", "She said she's proud. I didn't know I needed that."], "punchline": "Moms know everything."},
    {"hook": "went to work", "body": ["Three meetings. Two could be emails. One could be a text.", "My boss said we're family. Families don't fire you on Zoom.", "I stared at my screen for 8 hours. It stared back."], "punchline": "I work to live. I work to pay for things to work."},
    {"hook": "tried to be healthy", "body": ["I bought a salad. It cost more than Netflix.", "I went for a run. My lungs asked why.", "I drank water. Pure. Clean. Boring. I miss soda."], "punchline": "My body is a temple. That wants pizza."},
    {"hook": "checked social media", "body": ["Everyone is successful. Everyone is on vacation. I'm eating toast.", "I posted a picture. 3 likes. Mom. A bot. An accident.", "Comparison is the thief of joy. But still."], "punchline": "I closed the app. My toast was cold. Life goes on."}
]

HASHTAGS = "#mewonen #relatable #humor #life #mood #viral #fyp"

def send_telegram_message(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
    except: pass

def send_telegram_video(video_path, caption):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
        with open(video_path, "rb") as f:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"video": f}, timeout=60)
        return True
    except: return False

def generate_script():
    t = random.choice(SCRIPT_TEMPLATES)
    b = random.choice(t["body"])
    return f"Mewonen. Somewhere in the world.\n\nToday I {t['hook']}.\n\n{b}\n\n{t['punchline']}\n\nSee you tomorrow. Maybe."

def generate_voice(script):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
        r = requests.post(url, headers=headers, json={"text": script, "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}, timeout=30)
        if r.status_code == 200:
            p = "/tmp/audio.mp3"
            with open(p, "wb") as f: f.write(r.content)
            return p
        return None
    except: return None

def get_background():
    queries = ["city night", "sunset sky", "rain window", "quiet morning", "clouds", "empty street", "coffee shop"]
    q = random.choice(queries)
    try:
        url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q={q}&per_page=5&orientation=vertical"
        r = requests.get(url, timeout=10)
        hits = r.json().get("hits", [])
        if not hits: return None
        v = random.choice(hits).get("videos", {})
        for s in ["large", "medium", "small", "tiny"]:
            if s in v:
                r2 = requests.get(v[s]["url"], timeout=30)
                p = "/tmp/bg.mp4"
                with open(p, "wb") as f: f.write(r2.content)
                return p
        return None
    except: return None

def create_video(audio_path, bg_path, script):
    try:
        audio = AudioFileClip(audio_path)
        dur = audio.duration + 0.5
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
    send_telegram_message("🎬 Mewonen Engine — Starting...")
    script = generate_script()
    audio = generate_voice(script)
    if not audio: send_telegram_message("❌ Voice failed"); return
    bg = get_background()
    video = create_video(audio, bg, script)
    if not video: send_telegram_message("❌ Video failed"); return
    caption = f"{script.split(chr(10))[2]}\n\n💜 mewonnen.com\n\n{HASHTAGS}"
    ok = send_telegram_video(video, caption)
    if ok: send_telegram_message(f"✅ Posted!\n\n📝 {script[:150]}...")
    else: send_telegram_message("❌ Post failed")

if __name__ == "__main__":
    main()
