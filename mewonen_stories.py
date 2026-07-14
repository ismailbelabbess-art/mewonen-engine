import os, random, requests
from moviepy import *

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("MEWONEN_VOICE_ID", "")
PEXELS_KEY = os.environ.get("PEXELS_KEY", "")
MEWONEN_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
MEWONEN_CHAT = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")

STORIES = [
    {
        "hook": "I DIDN'T REPLY",
        "reveal": "HE DIED THE NEXT DAY",
        "cta": "TELL THEM TODAY",
        "bg": "phone on table dark"
    },
    {
        "hook": "SHE SAID SHE WAS FINE",
        "reveal": "SHE WASN'T",
        "cta": "ASK TWICE",
        "bg": "woman alone window"
    },
    {
        "hook": "HE CALLED EVERY SUNDAY",
        "reveal": "THEN ONE SUNDAY HE DIDN'T",
        "cta": "CALL YOUR MOM",
        "bg": "elderly man phone"
    },
    {
        "hook": "I SAW HER CRYING",
        "reveal": "SHE SAID IT WAS ALLERGIES",
        "cta": "HUG SOMEONE TODAY",
        "bg": "person crying window"
    },
    {
        "hook": "HE WORKED EVERY DAY",
        "reveal": "HE MISSED HER CHILDHOOD",
        "cta": "TIME IS EVERYTHING",
        "bg": "father office desk"
    },
    {
        "hook": "SHE POSTED A SMILE",
        "reveal": "SHE DELETED IT AN HOUR LATER",
        "cta": "CHECK ON YOUR FRIENDS",
        "bg": "girl phone bed dark"
    },
    {
        "hook": "HE SAID HE'D COME BACK",
        "reveal": "HE NEVER DID",
        "cta": "KEEP YOUR PROMISES",
        "bg": "empty road sunset"
    },
    {
        "hook": "SHE WAITED BY THE DOOR",
        "reveal": "FOR SOMEONE WHO NEVER CAME",
        "cta": "DON'T MAKE PEOPLE WAIT",
        "bg": "door open empty"
    }
]

def msg(text):
    try: requests.post(f"https://api.telegram.org/bot{MEWONEN_TOKEN}/sendMessage", json={"chat_id": MEWONEN_CHAT, "text": text}, timeout=10)
    except: pass

def send_vid(path, caption):
    try:
        with open(path, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{MEWONEN_TOKEN}/sendVideo", data={"chat_id": MEWONEN_CHAT, "caption": caption}, files={"video": f}, timeout=60)
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

def get_bg(query):
    try:
        r = requests.get(f"https://api.pexels.com/videos/search?query={query}&per_page=3&orientation=portrait", headers={"Authorization": PEXELS_KEY}, timeout=10)
        hits = r.json().get("videos", [])
        if not hits: return None
        v = random.choice(hits).get("video_files", [])
        for s in v:
            if s.get("width", 0) <= 1080:
                r2 = requests.get(s["link"], timeout=30)
                p = "/tmp/bg.mp4"
                with open(p, "wb") as f: f.write(r2.content)
                return p
    except: pass
    return None

def make_story_video(bg_path, hook, reveal, cta):
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        if bg_path:
            bg = VideoFileClip(bg_path)
            bg = bg.resized(height=1920)
            if bg.w > 1080: bg = bg.cropped(x_center=bg.w/2, width=1080)
            dur = 4
            if bg.duration < dur:
                repeats = int(dur / bg.duration) + 1
                clips = [bg] * repeats
                bg = concatenate_videoclips(clips).with_duration(dur)
            else:
                bg = bg.with_duration(dur)
        else:
            bg = ColorClip(size=(1080, 1920), color=(5,5,15), duration=4)
        
        def make_text_img(text, font_size=120):
            img = Image.new("RGBA", (1080, 400), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            draw.text((540 - tw//2, 50), text, fill=(255, 255, 255), font=font)
            path = f"/tmp/text_{random.randint(1,9999)}.png"
            img.save(path)
            return path
        
        t1_path = make_text_img(hook, 140)
        t2_path = make_text_img(reveal, 130)
        t3_path = make_text_img(cta, 100)
        t4_path = make_text_img("mewonen.com 💜", 80)
        
        t1 = ImageClip(t1_path, duration=1.5).with_position("center")
        t2 = ImageClip(t2_path, duration=1.5).with_position("center").with_start(1.5)
        t3 = ImageClip(t3_path, duration=0.7).with_position("center").with_start(3)
        t4 = ImageClip(t4_path, duration=0.3).with_position("center").with_start(3.7)
        
        final = CompositeVideoClip([bg, t1, t2, t3, t4])
        
        out = "/tmp/story.mp4"
        final.write_videofile(out, codec='libx264', fps=24, preset='ultrafast', threads=2, logger=None)
        bg.close(); final.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        return None

def main():
    msg("🎬 Mewonen Stories - Starting...")
    s = random.choice(STORIES)
    bg = get_bg(s["bg"])
    video = make_story_video(bg, s["hook"], s["reveal"], s["cta"])
    if not video: msg("Video failed"); return
    cap = f"{s['hook']}\n\n{s['reveal']}\n\n💜 mewonen.com\n\n#MewonenStories #Emotional #FYP"
    send_vid(video, cap)
    msg(f"✅ Posted: {s['hook']}")

if __name__ == "__main__":
    main()
