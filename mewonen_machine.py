import os, random, requests
from moviepy import *

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("MEWONEN_VOICE_ID", "")
PIXABAY_KEY = os.environ.get("PIXABAY_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")

TEMPLATES = [
    {
        "h": "checked my bank account",
        "b": ["The number stared back at me. No emotion. Just... nothing.", "I closed the app. Opened it again. Still nothing."],
        "p": "Money is just numbers on a screen. But those numbers control my life.",
        "bg": "city night"
    },
    {
        "h": "tried to talk to someone today",
        "b": ["I said hello. They looked at their phone. I became invisible.", "200 friends online. Zero in real life."],
        "p": "We're more connected than ever. And more alone than ever.",
        "bg": "coffee shop"
    },
    {
        "h": "read the news again",
        "b": ["Everything is burning. Everything is dying. Here's a funny cat.", "I don't know how to feel anymore. So I scroll."],
        "p": "The world is heavy. But I keep carrying it.",
        "bg": "city night"
    },
    {
        "h": "stepped outside",
        "b": ["The heat hit me like a wall. The sun doesn't care about my plans.", "A bird looked at me. I think it knew I was struggling."],
        "p": "Nature doesn't judge. It just... is.",
        "bg": "sunset sky"
    },
    {
        "h": "couldn't sleep again",
        "b": ["My brain decided to replay every mistake. Every embarrassing moment. Every what-if.", "3am. The world is asleep. I'm here. With my thoughts."],
        "p": "Tomorrow I'll be tired. But I'll try again.",
        "bg": "night sky"
    },
    {
        "h": "tried to find love",
        "b": ["Swipe. Swipe. Swipe. Hope. Disappointment. Repeat.", "Someone asked what I do for fun. I said 'survive.' They unmatched."],
        "p": "Maybe love isn't an algorithm. Maybe it's just... time.",
        "bg": "coffee shop"
    },
    {
        "h": "called my mom",
        "b": ["Her voice. That warmth. She asked if I'm okay. I said yes. I lied.", "She knew. Moms always know."],
        "p": "No matter how old I get, her voice makes me feel... safe.",
        "bg": "quiet morning"
    },
    {
        "h": "went to work",
        "b": ["Sitting. Staring. Typing. Pretending to care.", "My boss said 'great job.' I did nothing. Nothing matters."],
        "p": "I work to live. But sometimes I forget to live.",
        "bg": "city night"
    },
    {
        "h": "tried to take care of myself",
        "b": ["I drank water. I stretched. I breathed.", "It's hard. Being kind to yourself. Harder than it should be."],
        "p": "But I tried. That counts. Right?",
        "bg": "quiet morning"
    },
    {
        "h": "checked my phone 47 times today",
        "b": ["Nothing important. Just habit. Just... emptiness.", "I put it down. Picked it up. Put it down again."],
        "p": "One day, I'll learn to just... be.",
        "bg": "empty street"
    }
]

def msg(text):
    try: requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
    except: pass

def send_vid(path, caption):
    try:
        with open(path, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"video": f}, timeout=60)
        return True
    except: return False

def script():
    t = random.choice(TEMPLATES)
    b = random.choice(t["b"])
    return t, f"Mewonen. Somewhere in the world.\n\nToday I {t['h']}.\n\n{b}\n\n{t['p']}\n\nSee you tomorrow. Maybe."

def voice(text):
    try:
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
            headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
            json={"text": text, "voice_settings": {"stability": 0.55, "similarity_boost": 0.75, "speed": 0.9}},
            timeout=30
        )
        if r.status_code == 200:
            p = "/tmp/audio.mp3"
            with open(p, "wb") as f: f.write(r.content)
            return p
    except: pass
    return None

def bg_video(query):
    try:
        r = requests.get(f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q={query}&per_page=5&orientation=vertical", timeout=10)
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

def make_video(audio_path, bg_path):
    try:
        a = AudioFileClip(audio_path)
        dur = a.duration + 3
        if bg_path:
            v = VideoFileClip(bg_path)
            if v.duration < dur:
                repeats = int(dur / v.duration) + 1
                clips = [v] * repeats
                v = concatenate_videoclips(clips).with_duration(dur)
            else:
                v = v.with_duration(dur)
            v = v.resized(height=1920)
            if v.w > 1080: v = v.cropped(x_center=v.w/2, width=1080)
            if v.w < 1080: v = v.resized(width=1080)
        else:
            v = ColorClip(size=(1080, 1920), color=(10, 10, 24), duration=dur)
        v = v.with_audio(a)
        out = "/tmp/video.mp4"
        v.write_videofile(out, codec='libx264', audio_codec='aac', fps=24, preset='ultrafast', threads=2, logger=None)
        v.close(); a.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        return None

def main():
    msg("🎬 Mewonen Engine - Starting...")
    t, s = script()
    a = voice(s)
    if not a: msg("Voice failed"); return
    b = bg_video(t["bg"])
    v = make_video(a, b)
    if not v: msg("Video failed"); return
    cap = f"M E W O N E N\n\n{s.split(chr(10))[2]}\n\n💜 mewonnen.com\n\n#mewonen #relatable #feelings #viral"
    ok = send_vid(v, cap)
    if ok: msg(f"✅ Posted!\n\n{s[:150]}...")
    else: msg("Post failed")

if __name__ == "__main__":
    main()
