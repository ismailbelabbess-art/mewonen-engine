import os, random, requests
from moviepy import *

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("MEWONEN_VOICE_ID", "")
PEXELS_KEY = os.environ.get("PEXELS_KEY", "")
MEWONEN_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
MEWONEN_CHAT = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")
CALM_TOKEN = os.environ.get("CALM_TELEGRAM_BOT_TOKEN", "")
CALM_CHAT = os.environ.get("CALM_TELEGRAM_CHAT_ID", "")
SAMURAI_TOKEN = os.environ.get("SAMURAI_TELEGRAM_BOT_TOKEN", "")
SAMURAI_CHAT = os.environ.get("SAMURAI_TELEGRAM_CHAT_ID", "")

TEMPLATES = [
    {
        "en": "She sat alone in her apartment. Same walls. Same silence. Same emptiness. She opened mewonen.com. Drew a tear. Mewonen saw 🌧️. Someone understood.",
        "ja": "彼女はアパートで一人座っていた。同じ壁。同じ沈黙。同じ空虚。彼女はmewonen.comを開いた。涙を描いた。Mewonenは🌧️を見た。誰かが理解した。",
        "bg": "sad woman alone window"
    },
    {
        "en": "He walked home alone. Again. Headphones on. World off. 200 messages in the group chat. None for him. He drew his mood. Mewonen saw 🕳️. Someone noticed.",
        "ja": "彼は一人で家に帰った。また。ヘッドホンをつけて。世界を消して。グループチャットに200件のメッセージ。彼には1件もない。彼は気持ちを描いた。Mewonenは🕳️を見た。誰かが気づいた。",
        "bg": "sad man walking alone night"
    },
    {
        "en": "3am. She couldn't sleep. Her phone the only light. She typed 'why do I feel so alone'. Found mewonen.com. Drew a storm. Mewonen saw 🌪️. The storm passed.",
        "ja": "午前3時。彼女は眠れなかった。スマホだけが明かり。「なぜこんなに孤独なんだろう」と検索した。mewonen.comを見つけた。嵐を描いた。Mewonenは🌪️を見た。嵐は過ぎ去った。",
        "bg": "woman in bed awake night"
    },
    {
        "en": "He hadn't spoken to anyone in 3 days. Not a call. Not a text. Just silence. He opened mewonen.com. Drew a sun. Mewonen saw ☀️. He smiled. Just a little.",
        "ja": "彼は3日間誰とも話さなかった。電話もメッセージもない。ただの沈黙。彼はmewonen.comを開いた。太陽を描いた。Mewonenは☀️を見た。彼は少しだけ微笑んだ。",
        "bg": "lonely man sitting room"
    },
    {
        "en": "She smiled at work. Everyone thought she was fine. At home, she drew her real mood. Mewonen saw 🌧️. Finally, someone saw the truth.",
        "ja": "彼女は職場で微笑んだ。みんな大丈夫だと思った。家で、彼女は本当の気持ちを描いた。Mewonenは🌧️を見た。ついに、誰かが真実を見た。",
        "bg": "sad woman looking window"
    },
    {
        "en": "He posted a happy photo. Got 47 likes. Deleted it an hour later. Drew his real face. Mewonen saw 🌙. The mask fell off.",
        "ja": "彼は幸せそうな写真を投稿した。47のいいね。1時間後に削除した。本当の顔を描いた。Mewonenは🌙を見た。仮面が外れた。",
        "bg": "man looking phone sad"
    }
]

def msg(token, chat, text):
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat, "text": text}, timeout=10)
    except: pass

def send_vid(token, chat, path, caption):
    try:
        with open(path, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{token}/sendVideo", data={"chat_id": chat, "caption": caption}, files={"video": f}, timeout=60)
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

def get_bg(query):
    try:
        r = requests.get(f"https://api.pexels.com/videos/search?query={query}&per_page=3&orientation=portrait", headers={"Authorization": PEXELS_KEY}, timeout=10)
        hits = r.json().get("videos", [])
        if hits:
            v = random.choice(hits).get("video_files", [])
            for s in v:
                if s.get("width", 0) <= 1080:
                    r2 = requests.get(s["link"], timeout=30)
                    p = "/tmp/bg.mp4"
                    with open(p, "wb") as f: f.write(r2.content)
                    return p
    except: pass
    
    try:
        r = requests.get(f"https://api.pexels.com/v1/search?query={query}&per_page=3&orientation=portrait", headers={"Authorization": PEXELS_KEY}, timeout=10)
        photos = r.json().get("photos", [])
        if photos:
            img_url = random.choice(photos)["src"]["medium"]
            r2 = requests.get(img_url, timeout=20)
            p = "/tmp/bg.jpg"
            with open(p, "wb") as f: f.write(r2.content)
            return p
    except: pass
    return None

def make_video(audio_path, bg_path):
    try:
        a = AudioFileClip(audio_path)
        dur = a.duration + 2
        if bg_path and bg_path.endswith(".mp4"):
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
        elif bg_path:
            v = ImageClip(bg_path, duration=dur).resized(height=1920)
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
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, "🌧️ Loneliness Machine - Starting...")
    t = random.choice(TEMPLATES)
    en_audio = voice(t["en"])
    ja_audio = voice(t["ja"])
    if not en_audio: msg(MEWONEN_TOKEN, MEWONEN_CHAT, "Voice failed"); return
    bg = get_bg(t["bg"])
    en_video = make_video(en_audio, bg)
    if not en_video: msg(MEWONEN_TOKEN, MEWONEN_CHAT, "Video failed"); return
    cap_en = f"🌧️ {t['en'][:100]}...\n\n💜 mewonen.com\n\n#Loneliness #MentalHealth #FYP"
    send_vid(MEWONEN_TOKEN, MEWONEN_CHAT, en_video, cap_en)
    if CALM_TOKEN and CALM_CHAT: send_vid(CALM_TOKEN, CALM_CHAT, en_video, cap_en)
    if ja_audio:
        ja_video = make_video(ja_audio, bg)
        if ja_video:
            cap_ja = f"🌧️ {t['ja'][:100]}...\n\n💜 mewonen.com\n\n#孤独 #メンタルヘルス"
            if SAMURAI_TOKEN and SAMURAI_CHAT: send_vid(SAMURAI_TOKEN, SAMURAI_CHAT, ja_video, cap_ja)
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, "✅ Posted!")

if __name__ == "__main__":
    main()
