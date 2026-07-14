import os, random, requests
from moviepy import *

PEXELS_KEY = os.environ.get("PEXELS_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("MEWONEN_VOICE_ID", "")
TELEGRAM_BOT_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")

SCRIPTS = [
    {
        "male": "I don't approach women anymore. I'm afraid of being called a creep.",
        "female": "I don't make the first move anymore. Every time I did, he stopped trying."
    },
    {
        "male": "I pretend I'm fine being single. Truth is, I'm terrified I'll die alone.",
        "female": "I pretend I'm fine. Truth is, I'm tired of giving everything and getting nothing."
    },
    {
        "male": "I was taught not to cry. So I smile. And I'm breaking inside.",
        "female": "I was taught to be nice. So I say nothing. And I'm screaming inside."
    },
    {
        "male": "I work 60 hours a week. Not for me. For them.",
        "female": "I do everything for everyone. And nobody asks if I'm okay."
    },
    {
        "male": "I still think about her. 3 years later. I never told anyone.",
        "female": "I still think about him. 3 years later. I pretend I've moved on."
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

def voice(text, pitch="normal"):
    """Génère la voix via ElevenLabs"""
    try:
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
            headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
            json={
                "text": text,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                    "speed": 0.9
                }
            },
            timeout=30
        )
        if r.status_code == 200:
            p = f"/tmp/audio_{random.randint(1,99999)}.mp3"
            with open(p, "wb") as f: f.write(r.content)
            return p
    except: pass
    return None

def get_face_video(query):
    """Cherche une vidéo de visage sur Pexels"""
    try:
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation=portrait&size=small"
        r = requests.get(url, headers={"Authorization": PEXELS_KEY}, timeout=10)
        videos = r.json().get("videos", [])
        if not videos:
            return None
        v = random.choice(videos)
        files = v.get("video_files", [])
        # Prendre le fichier le plus léger
        best = None
        for f in files:
            if f.get("width", 0) <= 720:
                best = f
                break
        if not best and files:
            best = files[-1]
        if best:
            r2 = requests.get(best["link"], timeout=30)
            p = f"/tmp/face_{random.randint(1,99999)}.mp4"
            with open(p, "wb") as f: f.write(r2.content)
            return p
    except: pass
    return None

def make_video(male_audio, female_audio, male_text, female_text):
    """Crée la vidéo finale avec écran divisé"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Durée basée sur les audios
        a_m = AudioFileClip(male_audio)
        a_f = AudioFileClip(female_audio)
        
        # Fond divisé bleu/rose
        img = Image.new("RGB", (1080, 1920), "#000000")
        draw = ImageDraw.Draw(img)
        
        # Moitié gauche (bleu)
        for y in range(1920):
            r = int(10 + (y/1920)*25)
            g = int(20 + (y/1920)*50)
            b = int(50 + (y/1920)*80)
            draw.line([(0, y), (540, y)], fill=(r, g, b))
        
        # Moitié droite (rose)
        for y in range(1920):
            r = int(50 + (y/1920)*80)
            g = int(10 + (y/1920)*25)
            b = int(30 + (y/1920)*55)
            draw.line([(540, y), (1080, y)], fill=(r, g, b))
        
        # Ligne centrale
        draw.line([(540, 0), (540, 1920)], fill=(255, 255, 255, 60), width=3)
        
        try:
            font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
            font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        except:
            font_big = font_sm = ImageFont.load_default()
        
        # Labels
        draw.text((200, 80), "HIS SIDE", fill=(255, 255, 255, 200), font=font_big)
        draw.text((650, 80), "HER SIDE", fill=(255, 255, 255, 200), font=font_big)
        
        # Texte homme (gauche)
        words = male_text.split()[:20]
        txt = " ".join(words)
        y = 300
        for line in [txt[i:i+20] for i in range(0, len(txt), 20)]:
            draw.text((40, y), line, fill=(255, 255, 255), font=font_sm)
            y += 45
        
        # Texte femme (droite)
        words = female_text.split()[:20]
        txt = " ".join(words)
        y = 300
        for line in [txt[i:i+20] for i in range(0, len(txt), 20)]:
            draw.text((580, y), line, fill=(255, 255, 255), font=font_sm)
            y += 45
        
        # Phrase finale
        draw.text((250, 1650), "Two sides. Same pain.", fill=(255, 255, 255, 220), font=font_big)
        draw.text((350, 1750), "@the.mirror.two", fill=(255, 255, 255, 120), font=font_sm)
        
        # Watermark
        draw.text((30, 1850), "© The Mirror", fill=(255, 255, 255, 50), font=font_sm)
        
        img_path = "/tmp/mirror_bg.png"
        img.save(img_path)
        
        # Créer la vidéo
        dur = a_m.duration + a_f.duration + 2
        bg = ImageClip(img_path, duration=dur)
        
        # Combiner les audios
        silence = AudioClip(duration=0.5, fps=44100)
        combined = concatenate_audioclips([a_m, silence, a_f])
        bg = bg.with_audio(combined)
        
        out = "/tmp/mirror.mp4"
        bg.write_videofile(out, codec='libx264', audio_codec='aac', fps=24, preset='ultrafast', threads=2, logger=None)
        bg.close()
        return out
        
    except Exception as e:
        print(f"Video error: {e}")
        # Fallback simple
        try:
            dur = a_m.duration + 2
            bg = ImageClip(img_path, duration=dur)
            bg = bg.with_audio(a_m)
            out = "/tmp/mirror.mp4"
            bg.write_videofile(out, codec='libx264', audio_codec='aac', fps=24, preset='ultrafast', threads=2, logger=None)
            bg.close()
            return out
        except:
            return None

def main():
    msg("🪞 The Mirror - Starting...")
    
    s = random.choice(SCRIPTS)
    
    # Générer les voix
    male_audio = voice(s["male"])
    female_audio = voice(s["female"])
    
    if not male_audio or not female_audio:
        msg("Voice failed")
        return
    
    # Créer la vidéo
    video = make_video(male_audio, female_audio, s["male"], s["female"])
    if not video:
        msg("Video failed")
        return
    
    cap = f"🪞 Two sides. Same pain.\n\n@the.mirror.two\n\n#TheMirror #Relationships #FYP"
    send_vid(video, cap)
    msg("✅ Posted!")

if __name__ == "__main__":
    main()
