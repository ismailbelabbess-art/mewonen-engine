import os, random, requests
from moviepy import *

PEXELS_KEY = os.environ.get("PEXELS_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")

FALLBACKS = [
    {"male": "I don't approach women anymore. I'm afraid of being called a creep.", "female": "I don't make the first move anymore. Every time I did, he stopped trying."},
    {"male": "I pretend I'm fine being single. Truth is, I'm terrified I'll die alone.", "female": "I pretend I'm fine. Truth is, I'm tired of giving everything and getting nothing back."},
    {"male": "I was taught not to cry. So I smile. And I'm breaking inside.", "female": "I was taught to be nice. So I say nothing. And I'm screaming inside."},
    {"male": "I work 60 hours a week. Not for me. For them.", "female": "I do everything for everyone. And nobody asks if I'm okay."},
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

def get_video(query):
    try:
        r = requests.get(f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation=portrait", headers={"Authorization": PEXELS_KEY}, timeout=10)
        hits = r.json().get("videos", [])
        if not hits: return None
        v = random.choice(hits).get("video_files", [])
        for s in v:
            if s.get("width", 0) <= 1080:
                r2 = requests.get(s["link"], timeout=30)
                p = f"/tmp/{random.randint(1,9999)}.mp4"
                with open(p, "wb") as f: f.write(r2.content)
                return p
    except: pass
    return None

def make_video(male_text, female_text):
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Vidéos de visages
        male_vid = get_video("man face expression") or get_video("man looking camera")
        female_vid = get_video("woman face expression") or get_video("woman looking camera")
        
        dur = 10
        
        if male_vid:
            mv = VideoFileClip(male_vid).resized(height=1920)
            if mv.w > 540: mv = mv.cropped(x_center=mv.w/2, width=540)
            if mv.duration < dur: mv = mv.loop(duration=dur) if hasattr(mv,'loop') else concatenate_videoclips([mv]*int(dur/mv.duration+1)).with_duration(dur)
            else: mv = mv.with_duration(dur)
        else:
            mv = ColorClip(size=(540, 1920), color=(13,59,102), duration=dur)
        
        if female_vid:
            fv = VideoFileClip(female_vid).resized(height=1920)
            if fv.w > 540: fv = fv.cropped(x_center=fv.w/2, width=540)
            if fv.duration < dur: fv = fv.loop(duration=dur) if hasattr(fv,'loop') else concatenate_videoclips([fv]*int(dur/fv.duration+1)).with_duration(dur)
            else: fv = fv.with_duration(dur)
        else:
            fv = ColorClip(size=(540, 1920), color=(102,29,59), duration=dur)
        
        mv = mv.with_position((0, 0))
        fv = fv.with_position((540, 0))
        
        # Texte
        def txt_clip(text, pos, start, duration):
            img = Image.new("RGBA", (1080, 100), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
            except:
                font = ImageFont.load_default()
            draw.text((20, 10), text, fill=(255,255,255), font=font)
            p = f"/tmp/txt_{random.randint(1,9999)}.png"
            img.save(p)
            return ImageClip(p, duration=duration).with_position(('center', pos), relative=True).with_start(start)
        
        t1 = txt_clip(male_text[:80], (0.88, 0), 0, 5)
        t2 = txt_clip(female_text[:80], (0.88, 0), 5, 5)
        t3 = txt_clip("Two sides. Same pain.", (0.94, 0), 0, 10)
        t4 = txt_clip("@the.mirror.two", (0.97, 0), 9, 1)
        
        final = CompositeVideoClip([mv, fv, t1, t2, t3, t4], size=(1080, 1920))
        out = "/tmp/mirror.mp4"
        final.write_videofile(out, codec='libx264', fps=24, preset='ultrafast', threads=2, logger=None)
        final.close(); mv.close(); fv.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        return None

def main():
    msg("🪞 The Mirror - Starting...")
    f = random.choice(FALLBACKS)
    video = make_video(f["male"], f["female"])
    if not video: msg("Video failed"); return
    cap = f"🪞 Two sides. Same pain.\n\n@the.mirror.two\n\n#TheMirror #Relationships #MenAndWomen #FYP"
    send_vid(video, cap)
    msg("✅ Posted!")

if __name__ == "__main__":
    main()
