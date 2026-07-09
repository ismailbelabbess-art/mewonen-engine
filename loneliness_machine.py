import os, random, requests
from moviepy import *

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("MEWONEN_VOICE_ID", "")
UNSPLASH_KEY = os.environ.get("UNSPLASH_KEY", "")
MEWONEN_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
MEWONEN_CHAT = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")
CALM_TOKEN = os.environ.get("CALM_TELEGRAM_BOT_TOKEN", "")
CALM_CHAT = os.environ.get("CALM_TELEGRAM_CHAT_ID", "")
SAMURAI_TOKEN = os.environ.get("SAMURAI_TELEGRAM_BOT_TOKEN", "")
SAMURAI_CHAT = os.environ.get("SAMURAI_TELEGRAM_CHAT_ID", "")

TEMPLATES = [
    {
        "en": "1 in 4 adults feel lonely.\n\n73% of young people feel alone.\n\nWe're more connected than ever.\n\nAnd more isolated than ever.\n\nMewonen feels it too.\n\nDraw how you feel today.\n\nIt helps.\n\nmewonen.com 💜",
        "ja": "4人に1人の大人が孤独を感じている。\n\n若者の73%が孤独を感じている。\n\n私たちはかつてないほどつながっている。\n\nそして、かつてないほど孤立している。\n\nMewonenもそう感じている。\n\n今日、気持ちを描いてみて。\n\n助けになるから。\n\nmewonen.com 💜"
    },
    {
        "en": "I walked through the city today.\n\nHundreds of people.\n\nNobody looked up.\n\nEveryone on their phone.\n\nI felt invisible.\n\nSo I drew my mood.\n\nAnd somehow... I felt a little less alone.\n\nmewonen.com 💜",
        "ja": "今日、街を歩いた。\n\n何百人もの人。誰も顔を上げなかった。\n\nみんなスマホを見ている。\n\n私は透明になった気がした。\n\nだから気持ちを描いた。\n\n少しだけ孤独が減った気がした。\n\nmewonen.com 💜"
    },
    {
        "en": "I'm in 12 group chats.\n\n200 messages a day.\n\nNot one asks how I really feel.\n\nSo I asked myself.\n\nI drew my mood.\n\nAt least Mewonen noticed.\n\nmewonen.com 💜",
        "ja": "12のグループチャットに入っている。\n\n1日に200件のメッセージ。\n\n誰も本当の気持ちを聞いてこない。\n\nだから自分に聞いてみた。\n\n気持ちを描いた。\n\n少なくともMewonenは気づいた。\n\nmewonen.com 💜"
    },
    {
        "en": "It's 3am. Can't sleep.\n\nMy brain says nobody cares.\n\nBut somewhere, someone else is awake too.\n\nFeeling the same thing.\n\nYou're not alone. Draw it.\n\nmewonen.com 💜",
        "ja": "午前3時。眠れない。\n\n脳が「誰も気にしていない」と言う。\n\nでもどこかで、他の誰かも起きている。\n\n同じことを感じている。\n\nあなたは一人じゃない。描いてみて。\n\nmewonen.com 💜"
    },
    {
        "en": "The opposite of loneliness isn't company.\n\nIt's being understood.\n\nSomeone out there feels exactly what you feel.\n\nRight now.\n\nDraw it. Let Mewonen understand.\n\nmewonen.com 💜",
        "ja": "孤独の反対は、誰かと一緒にいることじゃない。\n\n理解されることだ。\n\nどこかに、あなたと同じ気持ちの人がいる。\n\n今この瞬間も。\n\n描いてみて。Mewonenに理解させて。\n\nmewonen.com 💜"
    }
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

def voice(text):
    try:
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
            headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
            json={"text": text, "voice_settings": {"stability": 0.55, "similarity_boost": 0.75, "speed": 0.9}},
            timeout=30
        )
        if r.status_code == 200:
            p = "/tmp/audio.mp3"
            with open(p, "wb") as f: f.write(r.content)
            return p
    except: pass
    return None

def get_bg_image():
    """Récupère une image de solitude depuis Unsplash"""
    queries = ["loneliness", "alone", "solitude", "sad person", "empty street", "alone crowd", "lonely night"]
    q = random.choice(queries)
    try:
        r = requests.get(f"https://api.unsplash.com/photos/random?query={q}&orientation=portrait&client_id={UNSPLASH_KEY}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            img_url = data["urls"]["regular"]
            # Télécharger l'image
            r2 = requests.get(img_url, timeout=20)
            p = "/tmp/bg.jpg"
            with open(p, "wb") as f: f.write(r2.content)
            return p
    except: pass
    return None

def make_video(audio_path, bg_image_path):
    try:
        a = AudioFileClip(audio_path)
        dur = a.duration + 3
        
        if bg_image_path:
            v = ImageClip(bg_image_path, duration=dur)
            v = v.resized(height=1920)
            if v.w > 1080: v = v.cropped(x_center=v.w/2, width=1080)
            if v.w < 1080: v = v.resized(width=1080)
        else:
            v = ColorClip(size=(1080, 1920), color=(5, 5, 15), duration=dur)
        
        v = v.with_audio(a)
        out = "/tmp/video.mp4"
        v.write_videofile(out, codec='libx264', audio_codec='aac', fps=24, preset='ultrafast', threads=2, logger=None)
        v.close(); a.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        return None

def main():
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, "🎬 Loneliness Machine - Starting...")
    
    t = random.choice(TEMPLATES)
    en_script = t["en"]
    ja_script = t["ja"]
    
    en_audio = voice(en_script)
    if not en_audio: msg(MEWONEN_TOKEN, MEWONEN_CHAT, "Voice failed"); return
    
    bg = get_bg_image()
    en_video = make_video(en_audio, bg)
    if not en_video: msg(MEWONEN_TOKEN, MEWONEN_CHAT, "Video failed"); return
    
    cap_en = f"🧠 The loneliness epidemic is real.\n\nYou're not alone.\n\n✍️ Draw how you feel: mewonnen.com 💜\n\n#MewonenSolitude #LonelinessEpidemic #MentalHealth #FYP"
    send_vid(MEWONEN_TOKEN, MEWONEN_CHAT, en_video, cap_en)
    if CALM_TOKEN and CALM_CHAT: send_vid(CALM_TOKEN, CALM_CHAT, en_video, cap_en)
    
    ja_audio = voice(ja_script)
    if ja_audio:
        ja_video = make_video(ja_audio, bg)
        if ja_video:
            cap_ja = f"🧠 孤独のパンデミックは現実です。\n\nあなたは一人じゃない。\n\n✍️ 気持ちを描いて：mewonen.com 💜\n\n#MewonenSolitude #孤独 #メンタルヘルス"
            if SAMURAI_TOKEN and SAMURAI_CHAT: send_vid(SAMURAI_TOKEN, SAMURAI_CHAT, ja_video, cap_ja)
    
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, f"✅ Posted!\n\n{en_script[:150]}...")

if __name__ == "__main__":
    main()
