import os, random, requests
from moviepy import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("MEWONEN_VOICE_ID", "")
MEWONEN_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
MEWONEN_CHAT = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")
CALM_TOKEN = os.environ.get("CALM_TELEGRAM_BOT_TOKEN", "")
CALM_CHAT = os.environ.get("CALM_TELEGRAM_CHAT_ID", "")
SAMURAI_TOKEN = os.environ.get("SAMURAI_TELEGRAM_BOT_TOKEN", "")
SAMURAI_CHAT = os.environ.get("SAMURAI_TELEGRAM_CHAT_ID", "")

EMOTIONS = ["☀️", "🌧️", "🌪️", "🌈", "⚡", "🌙", "🔥", "🌱", "🙏", "💨", "🌫️", "❄️", "🕳️"]

TEMPLATES = [
    {
        "en": "Today I checked my bank account.\n\nThe number stared back at me. No emotion. Just nothing.\n\nMoney is just numbers on a screen. But those numbers control my life.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、銀行口座を確認した。\n\n数字が私を見つめ返した。感情はない。ただ、何もない。\n\nお金はただの画面上の数字。でもその数字が私の人生を支配している。\n\nまた明日。\n\n...\n\nたぶんね。",
        "emoji": "🕳️"
    },
    {
        "en": "Today I tried to talk to someone.\n\nI said hello. They looked at their phone. I became invisible.\n\nWe're more connected than ever. And more alone than ever.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、誰かと話そうとした。\n\nこんにちはと言った。相手はスマホを見た。私は透明になった。\n\n私たちはかつてないほど繋がっている。そして、かつてないほど孤独だ。\n\nまた明日。\n\n...\n\nたぶんね。",
        "emoji": "🌧️"
    },
    {
        "en": "Today I read the news again.\n\nEverything is burning. Everything is dying. Here's a funny cat.\n\nThe world is heavy. But I keep carrying it.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、またニュースを読んだ。\n\nすべてが燃えている。すべてが死んでいる。面白い猫の動画。\n\n世界は重い。でも私は運び続ける。\n\nまた明日。\n\n...\n\nたぶんね。",
        "emoji": "🌪️"
    },
    {
        "en": "Today I stepped outside.\n\nThe heat hit me like a wall. The sun doesn't care about my plans.\n\nNature doesn't judge. It just is.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、外に出た。\n\n暑さが壁のように襲ってきた。太陽は私の予定を気にしない。\n\n自然は判断しない。ただ、そこにあるだけ。\n\nまた明日。\n\n...\n\nたぶんね。",
        "emoji": "🔥"
    },
    {
        "en": "Today I couldn't sleep again.\n\nMy brain replayed every mistake. Every embarrassing moment. Every what-if.\n\nTomorrow I'll be tired. But I'll try again.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、また眠れなかった。\n\n脳がすべての失敗を再生した。恥ずかしい瞬間。もしもの話。\n\n明日は疲れているだろう。でもまた挑戦する。\n\nまた明日。\n\n...\n\nたぶんね。",
        "emoji": "🌙"
    },
    {
        "en": "Today I tried to find love.\n\nSwipe. Swipe. Swipe. Hope. Disappointment. Repeat.\n\nMaybe love isn't an algorithm. Maybe it's just time.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、愛を探そうとした。\n\nスワイプ。スワイプ。スワイプ。期待。失望。繰り返し。\n\n愛はアルゴリズムじゃないのかもしれない。たぶん、ただの時間。\n\nまた明日。\n\n...\n\nたぶんね。",
        "emoji": "💨"
    },
    {
        "en": "Today I called my mom.\n\nHer voice. That warmth. She asked if I'm okay. I said yes. I lied.\n\nNo matter how old I get, her voice makes me feel safe.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、母に電話した。\n\n彼女の声。その温かさ。大丈夫かと聞かれた。はいと答えた。嘘をついた。\n\nいくつになっても、母の声は私を安心させる。\n\nまた明日。\n\n...\n\nたぶんね。",
        "emoji": "🙏"
    },
    {
        "en": "Today I went to work.\n\nSitting. Staring. Typing. Pretending to care.\n\nI work to live. But sometimes I forget to live.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、仕事に行った。\n\n座って。見つめて。タイピング。関心があるふり。\n\n生きるために働く。でも時々、生きることを忘れる。\n\nまた明日。\n\n...\n\nたぶんね。",
        "emoji": "🌫️"
    },
    {
        "en": "Today I tried to take care of myself.\n\nI drank water. I stretched. I breathed.\n\nBut I tried. That counts. Right?\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、自分を大切にしようとした。\n\n水を飲んだ。ストレッチした。呼吸した。\n\nでも挑戦した。それで十分。そうでしょ？\n\nまた明日。\n\n...\n\nたぶんね。",
        "emoji": "🌱"
    },
    {
        "en": "Today I checked my phone 47 times.\n\nNothing important. Just habit. Just emptiness.\n\nOne day, I'll learn to just be.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、47回スマホをチェックした。\n\n何も重要じゃない。ただの習慣。ただの空虚。\n\nいつか、ただ存在することを学ぶだろう。\n\nまた明日。\n\n...\n\nたぶんね。",
        "emoji": "❄️"
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

def create_background(emoji, phrase):
    """Crée un fond style appli Mewonen avec l'émotion"""
    try:
        img = Image.new("RGB", (1080, 1920), "#0a0a18")
        draw = ImageDraw.Draw(img)
        
        # Cercle décoratif (style canvas)
        draw.ellipse([290, 400, 790, 900], outline=(167, 139, 250, 60), width=3)
        
        # Émoji au centre
        try:
            font_e = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoEmoji-Regular.ttf", 180)
        except:
            font_e = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), emoji, font=font_e)
        ex = 540 - (bbox[2] - bbox[0]) // 2
        ey = 500
        draw.text((ex, ey), emoji, fill="#ffffff", font=font_e)
        
        # Phrase en bas
        try:
            font_p = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        except:
            font_p = ImageFont.load_default()
        
        words = phrase.split()[:6]
        short_phrase = " ".join(words)
        bbox = draw.textbbox((0, 0), short_phrase, font=font_p)
        px = 540 - (bbox[2] - bbox[0]) // 2
        draw.text((px, 1000), short_phrase, fill="#a78bfa", font=font_p)
        
        # Logo Mewonen
        draw.text((460, 150), "M E W O N E N", fill=(167, 139, 250), font=font_p)
        
        # URL
        draw.text((400, 1750), "mewonen.com", fill=(100, 100, 100), font=font_p)
        
        # Bouton simulé
        draw.rounded_rectangle([340, 1650, 740, 1720], radius=25, fill=(124, 58, 237, 255))
        draw.text((380, 1658), "Draw your mood", fill="white", font=font_p)
        
        bg_path = "/tmp/bg.png"
        img.save(bg_path)
        return bg_path
    except Exception as e:
        print(f"BG error: {e}")
        return None

def make_video(audio_path, bg_image_path):
    try:
        a = AudioFileClip(audio_path)
        dur = a.duration + 3
        
        # Créer un fond à partir de l'image
        bg_clip = ImageClip(bg_image_path, duration=dur)
        bg_clip = bg_clip.resized(height=1920)
        if bg_clip.w > 1080: bg_clip = bg_clip.cropped(x_center=bg_clip.w/2, width=1080)
        
        bg_clip = bg_clip.with_audio(a)
        out = "/tmp/video.mp4"
        bg_clip.write_videofile(out, codec='libx264', audio_codec='aac', fps=24, preset='ultrafast', threads=2, logger=None)
        bg_clip.close(); a.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        return None

def main():
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, "🎬 Mewonen Engine - Starting...")
    
    t = random.choice(TEMPLATES)
    en_script = t["en"]
    ja_script = t["ja"]
    emoji = t["emoji"]
    
    # Phrase pour l'image (prend la 3ème ligne du script)
    en_lines = en_script.split('\n')
    phrase = en_lines[6] if len(en_lines) > 6 else en_lines[-1]
    
    # Créer le fond style appli
    bg_image = create_background(emoji, phrase)
    if not bg_image:
        msg(MEWONEN_TOKEN, MEWONEN_CHAT, "Background failed")
        return
    
    # Version anglaise
    en_audio = voice(en_script)
    if not en_audio:
        msg(MEWONEN_TOKEN, MEWONEN_CHAT, "Voice failed")
        return
    
    en_video = make_video(en_audio, bg_image)
    if not en_video:
        msg(MEWONEN_TOKEN, MEWONEN_CHAT, "Video failed")
        return
    
    cap_en = f"🧠 What's your mood?\n\n✍️ Draw yours on mewonnen.com 💜\n\n#MewonenMood #relatable #feelings #viral #fyp"
    send_vid(MEWONEN_TOKEN, MEWONEN_CHAT, en_video, cap_en)
    if CALM_TOKEN and CALM_CHAT:
        send_vid(CALM_TOKEN, CALM_CHAT, en_video, cap_en)
    
    # Version japonaise
    ja_audio = voice(ja_script)
    if ja_audio:
        ja_video = make_video(ja_audio, bg_image)
        if ja_video:
            cap_ja = f"🧠 今日の気分は？\n\n✍️ mewonnen.com で描こう 💜\n\n#MewonenMood #気持ち #メンタルヘルス #viral"
            if SAMURAI_TOKEN and SAMURAI_CHAT:
                send_vid(SAMURAI_TOKEN, SAMURAI_CHAT, ja_video, cap_ja)
    
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, f"✅ Posted!\n\n{en_script[:150]}...")

if __name__ == "__main__":
    main()
