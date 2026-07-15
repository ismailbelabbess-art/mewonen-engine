import os, subprocess, random, requests
from moviepy import *

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("MEWONEN_VOICE_ID", "")
TELEGRAM_BOT_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")

REPLIES = [
    "She said she's fine. Her echo said she's not.",
    "He smiled. But his eyes were screaming.",
    "She laughed with everyone. And cried alone.",
    "He said he's over her. His echo still whispers her name.",
    "She posted a happy photo. Then deleted it an hour later."
]

VIRAL_VIDEOS = [
    "https://www.tiktok.com/@rewerggg/video/7550423289932320008",
    "https://www.tiktok.com/@feelingsunfiltered/video/7499812345678901234",
    "https://www.tiktok.com/@realemotions/video/7512345678901234567"
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

def download_video(url, output):
    try:
        subprocess.run(["yt-dlp", url, "-o", output, "--max-filesize", "10M"], check=True, capture_output=True, timeout=30)
        return os.path.exists(output)
    except: pass
    return False

def make_stitch(original_path, reply_audio):
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Vidéo originale (5 dernières secondes)
        orig = VideoFileClip(original_path)
        start = max(0, orig.duration - 5)
        orig = orig.subclip(start, orig.duration)
        orig = orig.resized(height=1920)
        if orig.w > 540: orig = orig.cropped(x_center=orig.w/2, width=540)
        
        # Fond bleu/rose pour la réponse
        reply_img = Image.new("RGB", (540, 1920), "#000000")
        draw = ImageDraw.Draw(reply_img)
        for y in range(1920):
            draw.line([(0,y),(540,y)], fill=(int(50+(y/1920)*80), int(10+(y/1920)*25), int(30+(y/1920)*55)))
        draw.text((80, 800), "Mewonen", fill=(255,255,255,150), font=ImageFont.load_default())
        draw.text((40, 1600), "mewonen.com", fill=(255,255,255,100), font=ImageFont.load_default())
        reply_path = "/tmp/reply_bg.png"
        reply_img.save(reply_path)
        
        # Audio de la réponse
        a = AudioFileClip(reply_audio)
        dur = a.duration + 1
        reply_clip = ImageClip(reply_path, duration=dur).with_audio(a)
        
        # Assembler
        orig = orig.with_position((0, 0))
        reply_clip = reply_clip.with_position((540, 0))
        
        final = CompositeVideoClip([orig, reply_clip], size=(1080, 1920))
        out = "/tmp/stitch.mp4"
        final.write_videofile(out, codec='libx264', audio_codec='aac', fps=24, preset='ultrafast', threads=2, logger=None)
        final.close(); orig.close(); reply_clip.close()
        return out
    except Exception as e:
        print(f"Stitch error: {e}")
        return None

def main():
    msg("🎬 Stitch Machine - Starting...")
    
    # Choisir une vidéo virale
    url = random.choice(VIRAL_VIDEOS)
    original_path = "/tmp/original.mp4"
    
    if not download_video(url, original_path):
        msg("Download failed")
        return
    
    # Générer la réponse
    reply = random.choice(REPLIES)
    audio = voice(reply)
    if not audio:
        msg("Voice failed")
        return
    
    # Créer le Stitch
    stitch = make_stitch(original_path, audio)
    if not stitch:
        msg("Stitch failed")
        return
    
    cap = f"🪞 {reply}\n\n💜 mewonen.com\n\n#Mewonen #Stitch #Emotions #FYP"
    send_vid(stitch, cap)
    msg("✅ Stitch posted!")

if __name__ == "__main__":
    main()
