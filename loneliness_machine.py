import os, random, requests
from moviepy import *

PEXELS_KEY = os.environ.get("PEXELS_KEY", "")
MEWONEN_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
MEWONEN_CHAT = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")
CALM_TOKEN = os.environ.get("CALM_TELEGRAM_BOT_TOKEN", "")
CALM_CHAT = os.environ.get("CALM_TELEGRAM_CHAT_ID", "")
SAMURAI_TOKEN = os.environ.get("SAMURAI_TELEGRAM_BOT_TOKEN", "")
SAMURAI_CHAT = os.environ.get("SAMURAI_TELEGRAM_CHAT_ID", "")

TEMPLATES = [
    {"text": "She sat alone. Same walls. Same silence.", "bg": "sad woman alone window"},
    {"text": "He walked home alone. Again. No one noticed.", "bg": "sad man walking alone night"},
    {"text": "3am. She couldn't sleep. Just her thoughts.", "bg": "woman in bed awake night"},
    {"text": "He hadn't spoken to anyone in 3 days.", "bg": "lonely man sitting room"},
    {"text": "She smiled at work. Nobody knew the truth.", "bg": "sad woman looking window"},
    {"text": "He posted a happy photo. Then deleted it.", "bg": "man looking phone sad"}
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

def make_video(bg_path, text):
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        dur = 8
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
        
        # Ajouter le texte sur l'image
        txt_img = Image.new("RGBA", (1080, 200), (0,0,0,0))
        draw = ImageDraw.Draw(txt_img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            font = ImageFont.load_default()
        draw.text((40, 30), text, fill=(255,255,255), font=font)
        draw.text((40, 90), "mewonen.com 💜", fill=(167,139,250), font=font)
        txt_path = "/tmp/txt.png"
        txt_img.save(txt_path)
        
        txt_clip = ImageClip(txt_path, duration=dur).with_position(("center", 1500))
        final = CompositeVideoClip([v, txt_clip])
        
        out = "/tmp/video.mp4"
        final.write_videofile(out, codec='libx264', fps=24, preset='ultrafast', threads=2, logger=None)
        v.close(); final.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        return None

def main():
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, "🌧️ Loneliness - Starting...")
    t = random.choice(TEMPLATES)
    bg = get_bg(t["bg"])
    video = make_video(bg, t["text"])
    if not video: msg(MEWONEN_TOKEN, MEWONEN_CHAT, "Video failed"); return
    cap = f"🌧️ {t['text']}\n\n💜 mewonen.com\n\n#Loneliness #MentalHealth #FYP"
    send_vid(MEWONEN_TOKEN, MEWONEN_CHAT, video, cap)
    if CALM_TOKEN and CALM_CHAT: send_vid(CALM_TOKEN, CALM_CHAT, video, cap)
    if SAMURAI_TOKEN and SAMURAI_CHAT: send_vid(SAMURAI_TOKEN, SAMURAI_CHAT, video, cap)
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, "✅ Posted!")

if __name__ == "__main__":
    main()
