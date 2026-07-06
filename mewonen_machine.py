import os, random, requests
from moviepy import *

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("MEWONEN_VOICE_ID", "")
PIXABAY_KEY = os.environ.get("PIXABAY_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")

TEMPLATES = [
    {"h": "checked my bank account", "b": ["I looked at the number. It looked back at me.", "My balance and motivation are both low."], "p": "Money comes and goes. Mostly goes."},
    {"h": "tried to make friends", "b": ["I smiled. They stared at their phone.", "200 messages. None for me."], "p": "Maybe tomorrow. Or not."},
    {"h": "read the news", "b": ["Bad news. More bad news. A dog. The dog was fine.", "I scrolled 40 minutes. 47 new worries."], "p": "I closed the app. The world waited."},
    {"h": "went outside", "b": ["Too hot. Phone overheated. I overheated.", "A bird judged me."], "p": "Back inside. AC is my friend."},
    {"h": "tried to sleep", "b": ["2am. Mistakes since 2018. Replay.", "3am. Solved hunger. Forgot."], "p": "Alarm at 7. Aged 10 years."},
    {"h": "used a dating app", "b": ["50 swipes. One match. Selling crypto.", "Hobby: surviving. Unmatched."], "p": "Adopting another plant."},
    {"h": "called my mom", "b": ["Eating dry cereal. She asked if I eat well.", "Love life? My plant is thriving."], "p": "Moms know everything."},
    {"h": "went to work", "b": ["3 meetings. 2 could be emails. 1 a text.", "We're family. Families don't fire on Zoom."], "p": "I work to afford work."},
    {"h": "tried to be healthy", "b": ["Salad costs more than Netflix.", "I ran. Lungs questioned me."], "p": "Temple. Wants pizza."},
    {"h": "checked social media", "b": ["Everyone is winning. I'm eating toast.", "Posted. 3 likes. Mom. Bot. Accident."], "p": "Toast was cold. Life goes on."}
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
    return f"Mewonen. Somewhere in the world.\n\nToday I {t['h']}.\n\n{b}\n\n{t['p']}\n\nSee you tomorrow. Maybe."

def voice(text):
    try:
        r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}", headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}, json={"text": text, "voice_settings": {"stability": 0.3, "similarity_boost": 0.9, "speed": 0.85}}, timeout=30)
        if r.status_code == 200:
            p = "/tmp/audio.mp3"
            with open(p, "wb") as f: f.write(r.content)
            return p
    except: pass
    return None

def bg_video():
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

def make_video(audio_path, bg_path, script_text):
    try:
        a = AudioFileClip(audio_path)
        dur = a.duration + 2
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
        
        # Watermark Mewonen (top)
        wm_top = TextClip(text="M E W O N E N", font_size=30, color='white')
        wm_top = wm_top.with_opacity(0.5).with_position(('center', 0.05), relative=True).with_duration(dur)
        
        # URL (bottom)
        wm_url = TextClip(text="mewonen.com", font_size=28, color='white')
        wm_url = wm_url.with_opacity(0.6).with_position(('center', 0.92), relative=True).with_duration(dur)
        
        final = CompositeVideoClip([v, wm_top, wm_url])
        out = "/tmp/video.mp4"
        final.write_videofile(out, codec='libx264', audio_codec='aac', fps=24, preset='ultrafast', threads=2, logger=None)
        
        v.close(); a.close(); final.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        return None

def main():
    msg("🎬 Mewonen Engine - Starting...")
    s = script()
    a = voice(s)
    if not a: msg("Voice failed"); return
    b = bg_video()
    v = make_video(a, b, s)
    if not v: msg("Video failed"); return
    cap = f"Mewonen. Somewhere in the world.\n\n{s.split(chr(10))[2]}\n\n💜 mewonnen.com\n\n#mewonen #relatable #humor #viral"
    ok = send_vid(v, cap)
    if ok: msg(f"✅ Posted!\n\n{s[:150]}...")
    else: msg("Post failed")

if __name__ == "__main__":
    main()
