import os, subprocess, random, requests

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
    "https://www.tiktok.com/@rewerggg/video/7550423289932320008"
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

def make_stitch_ffmpeg(original_path, audio_path, output_path):
    """Utilise FFmpeg pour créer le Stitch"""
    try:
        # Créer une image de fond rose pour la partie réponse
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "color=c=#661d3b:s=540x1920:d=6",
            "-frames:v", "1", "/tmp/reply_bg.png"
        ], check=True, capture_output=True)
        
        # Créer la vidéo réponse (image + audio)
        subprocess.run([
            "ffmpeg", "-y",
            "-loop", "1", "-i", "/tmp/reply_bg.png",
            "-i", audio_path,
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "128k",
            "-pix_fmt", "yuv420p", "-t", "6",
            "-vf", "drawtext=text='Mewonen':fontcolor=white@0.5:fontsize=40:x=(w-text_w)/2:y=800,drawtext=text='mewonen.com':fontcolor=white@0.3:fontsize=30:x=(w-text_w)/2:y=1600",
            "/tmp/reply.mp4"
        ], check=True, capture_output=True)
        
        # Prendre les 5 dernières secondes de l'original
        subprocess.run([
            "ffmpeg", "-y",
            "-sseof", "-5", "-i", original_path,
            "-c:v", "libx264", "-c:a", "aac",
            "-vf", "scale=540:1920,crop=540:1920",
            "-t", "5", "/tmp/original_cut.mp4"
        ], check=True, capture_output=True)
        
        # Assembler gauche (original) + droite (réponse)
        subprocess.run([
            "ffmpeg", "-y",
            "-i", "/tmp/original_cut.mp4",
            "-i", "/tmp/reply.mp4",
            "-filter_complex", "[0:v]scale=540:1920[left];[1:v]scale=540:1920[right];[left][right]hstack=inputs=2",
            "-c:v", "libx264", "-preset", "ultrafast",
            "-c:a", "aac",
            output_path
        ], check=True, capture_output=True)
        
        return os.path.exists(output_path)
    except Exception as e:
        print(f"FFmpeg error: {e}")
        return False

def main():
    msg("🎬 Stitch Machine - Starting...")
    
    url = random.choice(VIRAL_VIDEOS)
    original_path = "/tmp/original.mp4"
    
    if not download_video(url, original_path):
        msg("Download failed")
        return
    
    reply = random.choice(REPLIES)
    audio = voice(reply)
    if not audio:
        msg("Voice failed")
        return
    
    output = "/tmp/stitch.mp4"
    if not make_stitch_ffmpeg(original_path, audio, output):
        msg("Stitch failed")
        return
    
    cap = f"🪞 {reply}\n\n💜 mewonen.com\n\n#Mewonen #Stitch #Emotions #FYP"
    send_vid(output, cap)
    msg("✅ Stitch posted!")

if __name__ == "__main__":
    main()
