import os, random, requests
from moviepy import *

PEXELS_KEY = os.environ.get("PEXELS_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")

FALLBACKS = [
    {"male": "I don't approach women anymore. I'm afraid of being called a creep.", "female": "I don't make the first move anymore. He stopped trying."},
    {"male": "I pretend I'm fine. Truth is, I'm terrified I'll die alone.", "female": "I pretend I'm fine. I'm tired of giving everything."},
    {"male": "I was taught not to cry. So I smile. And I'm breaking.", "female": "I was taught to be nice. So I say nothing."},
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

def get_image(query):
    try:
        r = requests.get(f"https://api.pexels.com/v1/search?query={query}&per_page=3&orientation=portrait", headers={"Authorization": PEXELS_KEY}, timeout=10)
        photos = r.json().get("photos", [])
        if not photos: return None
        url = random.choice(photos)["src"]["medium"]
        r2 = requests.get(url, timeout=20)
        p = "/tmp/face.jpg"
        with open(p, "wb") as f: f.write(r2.content)
        return p
    except: pass
    return None

def make_video(male_text, female_text):
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        male_img = get_image("man face portrait")
        female_img = get_image("woman face portrait")
        
        # Créer le fond divisé
        out_img = Image.new("RGB", (1080, 1920), "#000000")
        draw = ImageDraw.Draw(out_img)
        
        if male_img:
            m = Image.open(male_img).resize((540, 1920))
            out_img.paste(m, (0, 0))
        else:
            for y in range(1920): draw.line([(0,y),(540,y)], fill=(13,59,102))
        
        if female_img:
            f = Image.open(female_img).resize((540, 1920))
            out_img.paste(f, (540, 0))
        else:
            for y in range(1920): draw.line([(540,y),(1080,y)], fill=(102,29,59))
        
        # Ligne centrale
        draw.line([(540,0),(540,1920)], fill=(255,255,255,80), width=3)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            font = ImageFont.load_default()
        
        # Texte homme (bas à gauche)
        draw.text((20, 1700), male_text[:70], fill=(255,255,255), font=font)
        # Texte femme (bas à droite)
        draw.text((560, 1700), female_text[:70], fill=(255,255,255), font=font)
        # Final
        draw.text((250, 1820), "Two sides. Same pain.", fill=(255,255,255,200), font=font)
        # Watermark
        draw.text((30, 30), "© The Mirror", fill=(255,255,255,60), font=font)
        
        img_path = "/tmp/mirror_bg.png"
        out_img.save(img_path)
        
        bg = ImageClip(img_path, duration=10)
        out = "/tmp/mirror.mp4"
        bg.write_videofile(out, codec='libx264', fps=24, preset='ultrafast', threads=2, logger=None)
        bg.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        return None

def main():
    msg("🪞 The Mirror - Starting...")
    f = random.choice(FALLBACKS)
    video = make_video(f["male"], f["female"])
    if not video: msg("Video failed"); return
    cap = f"🪞 Two sides. Same pain.\n\n@the.mirror.two\n\n#TheMirror #Relationships #FYP"
    send_vid(video, cap)
    msg("✅ Posted!")

if __name__ == "__main__":
    main()
