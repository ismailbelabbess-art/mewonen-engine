import os, random, requests
from moviepy import *

PEXELS_KEY = os.environ.get("PEXELS_KEY", "")
MEWONEN_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
MEWONEN_CHAT = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")
CALM_TOKEN = os.environ.get("CALM_TELEGRAM_BOT_TOKEN", "")
CALM_CHAT = os.environ.get("CALM_TELEGRAM_CHAT_ID", "")
SAMURAI_TOKEN = os.environ.get("SAMURAI_TELEGRAM_BOT_TOKEN", "")
SAMURAI_CHAT = os.environ.get("SAMURAI_TELEGRAM_CHAT_ID", "")

QUERIES = [
    "confident man alone sad",
    "strong woman looking away",
    "teenager sitting alone",
    "old man staring window",
    "businessman alone thinking",
    "athlete sitting alone sad",
    "young woman confident sad",
    "elderly woman looking away",
    "soldier alone reflection",
    "student alone campus night"
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

def get_media():
    """Cherche vidéo, sinon image, sur Pexels"""
    q = random.choice(QUERIES)
    
    # Essayer vidéo Pexels
    try:
        r = requests.get(
            f"https://api.pexels.com/videos/search?query={q}&per_page=5&orientation=portrait&size=small",
            headers={"Authorization": PEXELS_KEY}, timeout=10
        )
        hits = r.json().get("videos", [])
        if hits:
            v = random.choice(hits).get("video_files", [])
            for f in v:
                if f.get("width", 0) <= 720:
                    r2 = requests.get(f["link"], timeout=30)
                    p = "/tmp/media.mp4"
                    with open(p, "wb") as fh: fh.write(r2.content)
                    return p, "video"
    except: pass
    
    # Fallback : image Pexels
    try:
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={q}&per_page=5&orientation=portrait",
            headers={"Authorization": PEXELS_KEY}, timeout=10
        )
        photos = r.json().get("photos", [])
        if photos:
            url = random.choice(photos)["src"]["large"]
            r2 = requests.get(url, timeout=20)
            p = "/tmp/media.jpg"
            with open(p, "wb") as fh: fh.write(r2.content)
            return p, "image"
    except: pass
    
    return None, None

def make_video(media_path, media_type):
    """Crée une vidéo avec zoom lent et filtre chaud"""
    try:
        dur = 10
        
        if media_type == "video":
            clip = VideoFileClip(media_path)
            if clip.duration < dur:
                n = int(dur / clip.duration) + 1
                clip = concatenate_videoclips([clip] * n).with_duration(dur)
            else:
                clip = clip.with_duration(dur)
            clip = clip.resized(height=1920)
            if clip.w > 1080: clip = clip.cropped(x_center=clip.w/2, width=1080)
            elif clip.w < 1080: clip = clip.resized(width=1080)
        else:
            clip = ImageClip(media_path, duration=dur).resized(height=1920)
            if clip.w > 1080: clip = clip.cropped(x_center=clip.w/2, width=1080)
        
        # Zoom lent (Ken Burns)
        def zoom(t):
            return 1 + (t / dur) * 0.08
        clip = clip.resized(zoom)
        
        # Filtre chaud (overlay doré)
        from PIL import Image, ImageDraw
        overlay = Image.new("RGBA", (clip.w, clip.h), (255, 200, 100, 20))
        overlay_path = "/tmp/overlay.png"
        overlay.save(overlay_path)
        overlay_clip = ImageClip(overlay_path, duration=dur).with_opacity(0.25)
        
        final = CompositeVideoClip([clip, overlay_clip])
        
        out = "/tmp/viral.mp4"
        final.write_videofile(out, codec='libx264', fps=24, preset='ultrafast', threads=2, logger=None)
        clip.close(); final.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        return None

def main():
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, "🎬 Viral Emotion - Starting...")
    
    media_path, media_type = get_media()
    if not media_path:
        msg(MEWONEN_TOKEN, MEWONEN_CHAT, "No media found")
        return
    
    video = make_video(media_path, media_type)
    if not video:
        msg(MEWONEN_TOKEN, MEWONEN_CHAT, "Video failed")
        return
    
    cap = f"💜 mewonen.com\n\n#emotional #feelings #mentalhealth #FYP"
    send_vid(MEWONEN_TOKEN, MEWONEN_CHAT, video, cap)
    if CALM_TOKEN and CALM_CHAT: send_vid(CALM_TOKEN, CALM_CHAT, video, cap)
    if SAMURAI_TOKEN and SAMURAI_CHAT: send_vid(SAMURAI_TOKEN, SAMURAI_CHAT, video, cap)
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, "✅ Posted!")

if __name__ == "__main__":
    main()
