import os, random, requests
from moviepy import *

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("MEWONEN_VOICE_ID", "")
PEXELS_KEY = os.environ.get("PEXELS_KEY", "")
CALM_TOKEN = os.environ.get("CALM_TELEGRAM_BOT_TOKEN", "")
CALM_CHAT = os.environ.get("CALM_TELEGRAM_CHAT_ID", "")

SCRIPTS = [
    # Homme-Femme — Amour safe
    {"script": "He looked at her across the table. Three years together. She was still the most beautiful thing he'd ever seen. He didn't say it. He just smiled. She smiled back. That was enough.", "type": "couple", "bg": "couple dinner table"},
    {"script": "She had a bad day. He didn't ask questions. He just made her tea and put on her favorite movie. Sometimes love is not words. It's tea and a movie.", "type": "couple", "bg": "couple home cozy"},
    {"script": "They were 19 when they met. Now they're 67. He still opens the door for her. She still laughs at his jokes. Even the ones she's heard a thousand times.", "type": "couple", "bg": "elderly couple park"},
    
    # Mère-Fils — Tendresse safe
    {"script": "He hadn't called his mom in two weeks. Work. Life. Excuses. When he finally did, she didn't complain. She just said: 'I knew you'd call when you were ready.' He smiled. She always knew.", "type": "mother son", "bg": "phone call home"},
    {"script": "She kept every drawing he made as a child. Every single one. He's 30 now. She still has them in a box under her bed. 'My treasures,' she calls them.", "type": "mother son", "bg": "mother looking at drawings"},
    
    # Père-Fille — Safe et positif
    {"script": "He taught her how to ride a bike. Holding the seat. Running behind her. Then letting go. She fell. He picked her up. 'Again,' she said. And he smiled. That's exactly what he wanted to hear.", "type": "father daughter", "bg": "father teaching bike"},
    {"script": "She got her first job. She called her dad. He didn't say much. But the next day, a package arrived. A pen. With her name engraved. 'For my daughter,' it said. She still uses it.", "type": "father daughter", "bg": "gift package pen"},
    
    # Frère-Soeur — Safe et touchant
    {"script": "They fought over everything as kids. The remote. The last cookie. Who sat in the front seat. Now they live in different countries. But every Sunday, they video call. Every Sunday. Without fail.", "type": "siblings", "bg": "siblings video call"},
    {"script": "She was nervous about her first day of high school. He was two years older. He didn't say anything. He just drew a little smiley face on her notebook. She still has it. 12 years later.", "type": "siblings", "bg": "school notebook smiley"}
]

def msg(text):
    try: requests.post(f"https://api.telegram.org/bot{CALM_TOKEN}/sendMessage", json={"chat_id": CALM_CHAT, "text": text}, timeout=10)
    except: pass

def send_vid(path, caption):
    try:
        with open(path, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{CALM_TOKEN}/sendVideo", data={"chat_id": CALM_CHAT, "caption": caption}, files={"video": f}, timeout=60)
        return True
    except: return False

def voice(text):
    try:
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
            headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
            json={"text": text, "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "speed": 0.9}},
            timeout=30
        )
        if r.status_code == 200:
            p = "/tmp/audio.mp3"
            with open(p, "wb") as f: f.write(r.content)
            return p
    except: pass
    return None

def get_bg_video(query):
    try:
        r = requests.get(f"https://api.pexels.com/videos/search?query={query}&per_page=3&orientation=portrait", headers={"Authorization": PEXELS_KEY}, timeout=10)
        hits = r.json().get("videos", [])
        if not hits: return None
        v = random.choice(hits).get("video_files", [])
        for s in v:
            if s.get("width", 0) <= 1080:
                r2 = requests.get(s["link"], timeout=30)
                p = "/tmp/bg.mp4"
                with open(p, "wb") as f: f.write(r2.content)
                return p
    except: pass
    return None

def make_video(audio_path, bg_path):
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
            v = ColorClip(size=(1080, 1920), color=(5,5,15), duration=dur)
        v = v.with_audio(a)
        out = "/tmp/video.mp4"
        v.write_videofile(out, codec='libx264', audio_codec='aac', fps=24, preset='ultrafast', threads=2, logger=None)
        v.close(); a.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        return None

def main():
    msg("💜 Calm Relations - Starting...")
    s = random.choice(SCRIPTS)
    audio = voice(s["script"])
    if not audio: msg("Voice failed"); return
    bg = get_bg_video(s["bg"])
    video = make_video(audio, bg)
    if not video: msg("Video failed"); return
    cap = f"💜 {s['script'][:100]}...\n\nmewonen.com\n\n#CalmChaos #Relations #Love #Family #FYP"
    send_vid(video, cap)
    msg(f"✅ Posted!")

if __name__ == "__main__":
    main()
