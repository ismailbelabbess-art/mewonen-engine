import os, random, requests, json
from moviepy import *

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("MEWONEN_VOICE_ID", "")
TELEGRAM_BOT_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")

# Messages de secours si aucun message réel n'est disponible
FALLBACKS = [
    {"male": "I don't approach women anymore. Not because I don't want to. Because I'm afraid of being called a creep.", "female": "I don't make the first move anymore. Not because I don't want to. Because every time I did, he stopped trying."},
    {"male": "I pretend I'm fine being single. Truth is, I'm terrified I'll die alone.", "female": "I pretend I'm fine being single. Truth is, I'm tired of giving everything and getting nothing back."},
    {"male": "I was taught not to cry. Not to show weakness. So I smile. And I'm breaking inside.", "female": "I was taught to be nice. To not make waves. So I say nothing. And I'm screaming inside."},
    {"male": "I work 60 hours a week. Not for me. For them. And they don't even know.", "female": "I do everything for everyone. Work. Home. Kids. And nobody asks if I'm okay."},
    {"male": "I still think about her. 3 years later. I never told anyone.", "female": "I still think about him. 3 years later. I pretend I've moved on."}
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

def make_video(male_text, female_text):
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Fond divisé bleu/rose
        img = Image.new("RGB", (1080, 1920), "#000000")
        draw = ImageDraw.Draw(img)
        
        # Côté gauche (bleu)
        for y in range(1920):
            r = int(10 + (y/1920)*30)
            g = int(20 + (y/1920)*60)
            b = int(50 + (y/1920)*90)
            draw.line([(0, y), (540, y)], fill=(r, g, b))
        
        # Côté droit (rose)
        for y in range(1920):
            r = int(50 + (y/1920)*90)
            g = int(10 + (y/1920)*30)
            b = int(30 + (y/1920)*60)
            draw.line([(540, y), (1080, y)], fill=(r, g, b))
        
        # Ligne centrale
        draw.line([(540, 0), (540, 1920)], fill=(255, 255, 255, 40), width=2)
        
        # Titre
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)
        except:
            font = ImageFont.load_default()
        
        draw.text((200, 100), "HIS SIDE", fill=(255, 255, 255, 180), font=font)
        draw.text((620, 100), "HER SIDE", fill=(255, 255, 255, 180), font=font)
        
        # Texte gauche (homme)
        words_m = male_text.split()[:30]
        male_display = " ".join(words_m)
        y = 400
        for line in [male_display[i:i+25] for i in range(0, len(male_display), 25)]:
            draw.text((60, y), line, fill=(255, 255, 255), font=font)
            y += 50
        
        # Texte droite (femme)
        words_f = female_text.split()[:30]
        female_display = " ".join(words_f)
        y = 400
        for line in [female_display[i:i+25] for i in range(0, len(female_display), 25)]:
            draw.text((580, y), line, fill=(255, 255, 255), font=font)
            y += 50
        
        # Phrase finale
        draw.text((350, 1700), "Two sides. Same pain.", fill=(255, 255, 255, 200), font=font)
        draw.text((420, 1800), "themirror.two", fill=(255, 255, 255, 80), font=font)
        
        img_path = "/tmp/mirror_bg.png"
        img.save(img_path)
        
        # Créer la vidéo silencieuse
        bg = ImageClip(img_path, duration=12)
        out = "/tmp/mirror.mp4"
        bg.write_videofile(out, codec='libx264', fps=24, preset='ultrafast', threads=2, logger=None)
        bg.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        return None

def main():
    msg("🪞 The Mirror - Starting...")
    
    # Choisir un message
    f = random.choice(FALLBACKS)
    male_text = f["male"]
    female_text = f["female"]
    
    video = make_video(male_text, female_text)
    if not video: msg("Video failed"); return
    
    cap = f"🪞 Two sides. Same pain.\n\nNew theme every day.\n\n#TheMirror #Relationships #MenAndWomen #FYP"
    send_vid(video, cap)
    msg("✅ Posted!")

if __name__ == "__main__":
    main()
