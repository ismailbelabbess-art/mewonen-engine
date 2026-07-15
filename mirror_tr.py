import os, random, requests
from moviepy import *

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("MEWONEN_VOICE_ID", "")
TELEGRAM_BOT_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")

SCRIPTS = [
    {
        "erkek": "Artık kadınlara yaklaşmıyorum. Tacizci olarak görülmekten korkuyorum.",
        "kadin": "Artık ilk adımı atmıyorum. Çünkü her attığımda, o durdu."
    },
    {
        "erkek": "Yalnız olmaktan iyiymiş gibi davranıyorum. Gerçek şu ki, yalnız ölmekten korkuyorum.",
        "kadin": "İyiymiş gibi davranıyorum. Gerçek şu ki, her şeyi verip hiçbir şey almaktan yoruldum."
    },
    {
        "erkek": "Bana ağlamamayı öğrettiler. Ben de gülümsüyorum. Ama içim paramparça.",
        "kadin": "Bana sessiz olmayı öğrettiler. Ben de susuyorum. Ama içim çığlık atıyor."
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

def voice(text):
    try:
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
            headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
            json={"text": text, "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "speed": 0.9}},
            timeout=30
        )
        if r.status_code == 200:
            p = f"/tmp/audio_{random.randint(1,99999)}.mp3"
            with open(p, "wb") as f: f.write(r.content)
            return p
    except: pass
    return None

def make_video(male_text, female_text, male_audio, female_audio):
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new("RGB", (1080, 1920), "#000000")
        draw = ImageDraw.Draw(img)
        
        for y in range(1920):
            r, g, b = int(10+(y/1920)*25), int(20+(y/1920)*50), int(50+(y/1920)*80)
            draw.line([(0,y), (540,y)], fill=(r,g,b))
            r, g, b = int(50+(y/1920)*80), int(10+(y/1920)*25), int(30+(y/1920)*55)
            draw.line([(540,y), (1080,y)], fill=(r,g,b))
        
        draw.line([(540,0), (540,1920)], fill=(255,255,255,60), width=3)
        
        try:
            font_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38)
            font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        except:
            font_b = font_s = ImageFont.load_default()
        
        draw.text((150, 80), "ERKEK", fill=(255,255,255,200), font=font_b)
        draw.text((650, 80), "KADIN", fill=(255,255,255,200), font=font_b)
        
        y = 300
        for line in [male_text[i:i+22] for i in range(0, len(male_text), 22)]:
            draw.text((40, y), line, fill=(255,255,255), font=font_s)
            y += 45
        
        y = 300
        for line in [female_text[i:i+22] for i in range(0, len(female_text), 22)]:
            draw.text((580, y), line, fill=(255,255,255), font=font_s)
            y += 45
        
        draw.text((220, 1650), "İki taraf. Aynı acı.", fill=(255,255,255,220), font=font_b)
        draw.text((400, 1800), "@the.mirror.two", fill=(255,255,255,100), font=font_s)
        draw.text((30, 1860), "© The Mirror", fill=(255,255,255,50), font=font_s)
        
        img_path = "/tmp/mirror_bg.png"
        img.save(img_path)
        
        a_m = AudioFileClip(male_audio)
        a_f = AudioFileClip(female_audio)
        dur = a_m.duration + a_f.duration + 2
        
        bg = ImageClip(img_path, duration=dur)
        
        silence = AudioClip(duration=0.5, fps=44100)
        combined = concatenate_audioclips([a_m, silence, a_f])
        bg = bg.with_audio(combined)
        
        out = "/tmp/mirror.mp4"
        bg.write_videofile(out, codec='libx264', audio_codec='aac', fps=24, preset='ultrafast', threads=2, logger=None)
        bg.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        return None

def main():
    msg("🪞 The Mirror TR - Starting...")
    s = random.choice(SCRIPTS)
    
    male_audio = voice(s["erkek"])
    female_audio = voice(s["kadin"])
    
    if not male_audio or not female_audio:
        msg("Voice failed")
        return
    
    video = make_video(s["erkek"], s["kadin"], male_audio, female_audio)
    if not video:
        msg("Video failed")
        return
    
    cap = f"🪞 İki taraf. Aynı acı.\n\n@the.mirror.two\n\n#TheMirror #İlişkiler #KadınErkek #FYP"
    send_vid(video, cap)
    msg("✅ Posted!")

if __name__ == "__main__":
    main()
