import os, random, requests
from moviepy import *

PEXELS_KEY = os.environ.get("PEXELS_KEY", "")
MEWONEN_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
MEWONEN_CHAT = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")
CALM_TOKEN = os.environ.get("CALM_TELEGRAM_BOT_TOKEN", "")
CALM_CHAT = os.environ.get("CALM_TELEGRAM_CHAT_ID", "")
SAMURAI_TOKEN = os.environ.get("SAMURAI_TELEGRAM_BOT_TOKEN", "")
SAMURAI_CHAT = os.environ.get("SAMURAI_TELEGRAM_CHAT_ID", "")

# Thèmes et phrases percutantes
THEMES = [
    {"query": "sad man alone", "text": "He hasn't spoken to anyone in 3 days."},
    {"query": "sad woman alone window", "text": "She smiled. Nobody knew the truth."},
    {"query": "lonely man walking night", "text": "Some people carry a sadness the world will never see."},
    {"query": "woman looking sad", "text": "She said she was fine. She wasn't."},
    {"query": "old couple in love", "text": "50 years. One love."},
    {"query": "elderly couple holding hands", "text": "Some bonds don't just last. They define you."},
    {"query": "man crying alone", "text": "He posted a happy photo. Deleted it an hour later."},
    {"query": "woman alone night window", "text": "3am. She couldn't sleep. Just her thoughts."},
    {"query": "couple in love sunset", "text": "This is what love looks like."},
    {"query": "lonely man sitting", "text": "He waited for a message that never came."}
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

def get_video(query):
    """Cherche une vidéo sur Pexels, sinon une image, sinon retourne None"""
    # Essayer vidéo
    try:
        r = requests.get(f"https://api.pexels.com/videos/search?query={query}&per_page=3&orientation=portrait&size=small", headers={"Authorization": PEXELS_KEY}, timeout=10)
        hits = r.json().get("videos", [])
        if hits:
            v = random.choice(hits).get("video_files", [])
            for s in v:
                if s.get("width", 0) <= 1080:
                    r2 = requests.get(s["link"], timeout=30)
                    p = "/tmp/bg.mp4"
                    with open(p, "wb") as f: f.write(r2.content)
                    return p, "video"
    except: pass
    
    # Essayer image
    try:
        r = requests.get(f"https://api.pexels.com/v1/search?query={query}&per_page=3&orientation=portrait", headers={"Authorization": PEXELS_KEY}, timeout=10)
        photos = r.json().get("photos", [])
        if photos:
            img_url = random.choice(photos)["src"]["large"]
            r2 = requests.get(img_url, timeout=20)
            p = "/tmp/bg.jpg"
            with open(p, "wb") as f: f.write(r2.content)
            return p, "image"
    except: pass
    return None, None

def make_video(bg_path, bg_type, text):
    """Crée la vidéo virale avec effet de zoom et texte"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        dur = 8
        
        # Charger le fond
        if bg_type == "video":
            clip = VideoFileClip(bg_path)
            if clip.duration < dur:
                repeats = int(dur / clip.duration) + 1
                clips = [clip] * repeats
                clip = concatenate_videoclips(clips).with_duration(dur)
            else:
                clip = clip.with_duration(dur)
            clip = clip.resized(height=1920)
            if clip.w > 1080:
                clip = clip.cropped(x_center=clip.w/2, width=1080)
            elif clip.w < 1080:
                clip = clip.resized(width=1080)
        else:
            clip = ImageClip(bg_path, duration=dur).resized(height=1920)
            if clip.w > 1080:
                clip = clip.cropped(x_center=clip.w/2, width=1080)
        
        # Effet de zoom lent (Ken Burns)
        def zoom_effect(t):
            return 1 + (t / dur) * 0.1  # Zoom de 10% sur la durée
        clip = clip.resized(zoom_effect)
        
        # Créer le texte superposé
        txt_img = Image.new("RGBA", (1080, 200), (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38)
        except:
            font = ImageFont.load_default()
        
        # Centrer le texte
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((1080 - tw) // 2, 40), text, fill=(255, 255, 255), font=font)
        draw.text(((1080 - 200) // 2, 120), "mewonen.com 💜", fill=(167, 139, 250, 200), font=font)
        txt_path = "/tmp/txt.png"
        txt_img.save(txt_path)
        
        txt_clip = ImageClip(txt_path, duration=dur).with_position(("center", 1500))
        
        # Assembler
        final = CompositeVideoClip([clip, txt_clip])
        out = "/tmp/viral.mp4"
        final.write_videofile(out, codec='libx264', fps=24, preset='ultrafast', threads=2, logger=None)
        clip.close(); final.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        return None

def main():
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, "🎬 Viral Emotion - Starting...")
    t = random.choice(THEMES)
    bg_path, bg_type = get_video(t["query"])
    if not bg_path:
        msg(MEWONEN_TOKEN, MEWONEN_CHAT, "No media found")
        return
    video = make_video(bg_path, bg_type, t["text"])
    if not video:
        msg(MEWONEN_TOKEN, MEWONEN_CHAT, "Video failed")
        return
    cap = f"{t['text']}\n\n💜 mewonen.com\n\n#emotional #feelings #loneliness #love #mentalhealth #FYP"
    send_vid(MEWONEN_TOKEN, MEWONEN_CHAT, video, cap)
    if CALM_TOKEN and CALM_CHAT: send_vid(CALM_TOKEN, CALM_CHAT, video, cap)
    if SAMURAI_TOKEN and SAMURAI_CHAT: send_vid(SAMURAI_TOKEN, SAMURAI_CHAT, video, cap)
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, "✅ Posted!")

if __name__ == "__main__":
    main()
