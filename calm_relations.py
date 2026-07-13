import os, random, requests
from moviepy import *

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("MEWONEN_VOICE_ID", "")
PEXELS_KEY = os.environ.get("PEXELS_KEY", "")
CALM_TOKEN = os.environ.get("CALM_TELEGRAM_BOT_TOKEN", "")
CALM_CHAT = os.environ.get("CALM_TELEGRAM_CHAT_ID", "")

SCRIPTS = [
    # Homme-Femme
    {"script": "He looked at her across the table. Three years together. She was still the most beautiful thing he'd ever seen. He didn't say it. He just smiled. She smiled back. That was enough.", "type": "couple", "bg": "couple dinner table"},
    {"script": "She was angry. He was silent. The argument had lasted an hour. Then he stood up, walked to the kitchen, and made her tea. The same way she liked it. She cried. Not because of the tea.", "type": "couple", "bg": "couple kitchen home"},
    {"script": "They met when they were 19. Now they're 67. He still holds her hand when they cross the street. She still laughs at his jokes. Even the bad ones.", "type": "couple", "bg": "elderly couple walking"},
    
    # Mère-Fils
    {"script": "He hadn't called his mom in two weeks. Work. Life. Excuses. When he finally did, she didn't complain. She just said: 'I knew you'd call when you were ready.' He cried after hanging up.", "type": "mother son", "bg": "phone call home"},
    {"script": "She watched her son sleep. He was 24 now. But to her, he was still the little boy who held her hand on the first day of school. She kissed his forehead. He didn't wake up. But he smiled.", "type": "mother son", "bg": "mother sleeping child"},
    
    # Père-Fille
    {"script": "He taught her how to ride a bike. How to drive. How to stand up for herself. Now she's getting married. He looks at her and sees the little girl who once fell asleep on his shoulder. He smiles. He doesn't cry. Not yet.", "type": "father daughter", "bg": "father daughter wedding"},
    {"script": "She called her dad at 2am. He answered on the first ring. 'I'm scared,' she said. 'I know,' he said. 'But I'm here.' They talked until sunrise.", "type": "father daughter", "bg": "phone call night"},
    
    # Frère-Soeur
    {"script": "They fought over everything as kids. Toys. TV. The last piece of cake. Now he's moving to another country. She hugs him at the airport. 'Don't forget me,' she says. 'Impossible,' he replies.", "type": "siblings", "bg": "airport goodbye"},
    {"script": "She was being bullied at school. He was two years older. He walked into the principal's office and didn't leave until they listened. That night, she made him a drawing. He still has it. 15 years later.", "type": "siblings", "bg": "brother sister home"}
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
            v = v.loop(duration=dur) if v.duration < dur else v.with_duration(dur)
            v = v.resized(height=1920)
            if v.w > 1080: v = v.cropped(x_center=v.w/2, width=1080)
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
