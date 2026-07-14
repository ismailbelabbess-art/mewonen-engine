import os, random, requests
from moviepy import *

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID_MALE = os.environ.get("VOICE_ID_MALE", "")
VOICE_ID_FEMALE = os.environ.get("VOICE_ID_FEMALE", "")
TELEGRAM_BOT_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")

FALLBACKS = [
    {"male": "I don't approach women anymore. Not because I don't want to. Because I'm afraid of being called a creep.", "female": "I don't make the first move anymore. Not because I don't want to. Because every time I did, he stopped trying."},
    {"male": "I pretend I'm fine being single. Truth is, I'm terrified I'll die alone.", "female": "I pretend I'm fine being single. Truth is, I'm tired of giving everything and getting nothing back."},
    {"male": "I was taught not to cry. So I smile. And I'm breaking inside.", "female": "I was taught to be nice. So I say nothing. And I'm screaming inside."},
    {"male": "I work 60 hours a week. Not for me. For them. And they don't even know.", "female": "I do everything for everyone. And nobody asks if I'm okay."},
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

def voice(text, voice_id):
    try:
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
            json={"text": text, "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "speed": 0.95}},
            timeout=30
        )
        if r.status_code == 200:
            p = f"/tmp/audio_{random.randint(1,9999)}.mp3"
            with open(p, "wb") as f: f.write(r.content)
            return p
    except: pass
    return None

def make_video(male_audio, female_audio):
    try:
        from PIL import Image, ImageDraw
        
        a_m = AudioFileClip(male_audio)
        a_f = AudioFileClip(female_audio)
        dur = a_m.duration + a_f.duration + 3
        
        # Fond bleu/rose
        img = Image.new("RGB", (1080, 1920), "#000000")
        draw = ImageDraw.Draw(img)
        for y in range(1920):
            draw.line([(0,y),(540,y)], fill=(13,59,102))
            draw.line([(540,y),(1080,y)], fill=(102,29,59))
        draw.line([(540,0),(540,1920)], fill=(255,255,255,60), width=3)
        bg_path = "/tmp/mirror_bg.png"
        img.save(bg_path)
        
        bg = ImageClip(bg_path, duration=dur)
        
        # Combiner les audios
        silence = AudioClip(duration=0.5, fps=44100)
        combined = concatenate_audioclips([a_m, silence, a_f])
        
        bg = bg.with_audio(combined)
        
        out = "/tmp/mirror_video.mp4"
        bg.write_videofile(out, codec='libx264', audio_codec='aac', fps=24, preset='ultrafast', threads=2, logger=None)
        bg.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        # Fallback : juste l'audio masculin
        try:
            bg = ImageClip(bg_path, duration=a_m.duration+2)
            bg = bg.with_audio(a_m)
            out = "/tmp/mirror_video.mp4"
            bg.write_videofile(out, codec='libx264', audio_codec='aac', fps=24, preset='ultrafast', threads=2, logger=None)
            bg.close()
            return out
        except:
            return None

def main():
    msg("🪞 The Mirror - Starting...")
    f = random.choice(FALLBACKS)
    
    male_audio = voice(f["male"], VOICE_ID_MALE)
    female_audio = voice(f["female"], VOICE_ID_FEMALE)
    
    if not male_audio or not female_audio:
        msg("Voice failed")
        return
    
    video = make_video(male_audio, female_audio)
    if not video: msg("Video failed"); return
    
    cap = f"🪞 Two sides. Same pain.\n\n@the.mirror.two\n\n#TheMirror #Relationships #MenAndWomen #FYP"
    send_vid(video, cap)
    msg("✅ Posted!")

if __name__ == "__main__":
    main()
