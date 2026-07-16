import os, random, requests
from moviepy import *

PIXABAY_KEY = os.environ.get("PIXABAY_KEY", "")
MEWONEN_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
MEWONEN_CHAT = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")
CALM_TOKEN = os.environ.get("CALM_TELEGRAM_BOT_TOKEN", "")
CALM_CHAT = os.environ.get("CALM_TELEGRAM_CHAT_ID", "")
SAMURAI_TOKEN = os.environ.get("SAMURAI_TELEGRAM_BOT_TOKEN", "")
SAMURAI_CHAT = os.environ.get("SAMURAI_TELEGRAM_CHAT_ID", "")

QUERIES = [
    "sad man alone",
    "sad woman alone",
    "lonely",
    "old couple in love",
    "elderly couple",
    "couple in love sunset",
    "lonely woman",
    "lonely man"
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

def get_image():
    q = random.choice(QUERIES)
    try:
        r = requests.get(f"https://pixabay.com/api/?key={PIXABAY_KEY}&q={q}&per_page=5&orientation=vertical&safesearch=true", timeout=10)
        hits = r.json().get("hits", [])
        if hits:
            img_url = random.choice(hits)["largeImageURL"]
            r2 = requests.get(img_url, timeout=20)
            p = "/tmp/bg.jpg"
            with open(p, "wb") as f: f.write(r2.content)
            return p
    except: pass
    return None

def make_video(bg_path):
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        dur = 8
        if bg_path:
            v = ImageClip(bg_path, duration=dur).resized(height=1920)
            if v.w > 1080: v = v.cropped(x_center=v.w/2, width=1080)
        else:
            v = ColorClip(size=(1080, 1920), color=(5,5,15), duration=dur)
        
        txt_img = Image.new("RGBA", (1080, 100), (0,0,0,0))
        draw = ImageDraw.Draw(txt_img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        except:
            font = ImageFont.load_default()
        draw.text((300, 20), "mewonen.com 💜", fill=(255,255,255,150), font=font)
        txt_path = "/tmp/txt.png"
        txt_img.save(txt_path)
        
        txt_clip = ImageClip(txt_path, duration=dur).with_position(("center", 1800))
        final = CompositeVideoClip([v, txt_clip])
        
        out = "/tmp/video.mp4"
        final.write_videofile(out, codec='libx264', fps=24, preset='ultrafast', threads=2, logger=None)
        v.close(); final.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        return None

def main():
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, "🎬 Loneliness Silent - Starting...")
    bg = get_image()
    if not bg: msg(MEWONEN_TOKEN, MEWONEN_CHAT, "No image found"); return
    video = make_video(bg)
    if not video: msg(MEWONEN_TOKEN, MEWONEN_CHAT, "Video failed"); return
    cap = f"💜 mewonen.com\n\n#Loneliness #MentalHealth #Emotions #FYP"
    send_vid(MEWONEN_TOKEN, MEWONEN_CHAT, video, cap)
    if CALM_TOKEN and CALM_CHAT: send_vid(CALM_TOKEN, CALM_CHAT, video, cap)
    if SAMURAI_TOKEN and SAMURAI_CHAT: send_vid(SAMURAI_TOKEN, SAMURAI_CHAT, video, cap)
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, "✅ Posted!")
