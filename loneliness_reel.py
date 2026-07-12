import os, random, requests
from moviepy import *

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("MEWONEN_VOICE_ID", "")
UNSPLASH_KEY = os.environ.get("UNSPLASH_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")

STORIES = [
    {
        "en": "She sat alone in her apartment.\n\nSame walls. Same silence. Same emptiness.\n\nBut today, she opened mewonnen.com.\n\nShe drew how she felt. A messy circle. Nothing special.\n\nMewonen saw 🌧️. 'Let it wash over you.'\n\nShe smiled. For the first time this week.\n\nSomeone understood.\n\nYou're next. 💜 mewonnen.com",
        "ja": "彼女はアパートに一人で座っていた。\n\n同じ壁。同じ沈黙。同じ空虚。\n\nでも今日、彼女はmewonen.comを開いた。\n\n気持ちを描いた。ただの丸。何の変哲もない。\n\nMewonenは🌧️を見た。「流れに任せて。」\n\n彼女は微笑んだ。今週初めて。\n\n誰かが理解してくれた。\n\n次はあなたです。💜 mewonnen.com"
    },
    {
        "en": "He walked home alone. Again.\n\nHeadphones on. World off.\n\n200 messages in the group chat. None for him.\n\nHe opened mewonnen.com.\n\nDrew a single line. That's all he had.\n\nMewonen saw 🕳️. 'Space waiting.'\n\nHe breathed. And drew another line. And another.\n\nSometimes, starting is everything.\n\nStart now. 💜 mewonnen.com",
        "ja": "彼は一人で家に帰った。また。\n\nヘッドホンをつけて。世界を消して。\n\nグループチャットに200件のメッセージ。彼には1件もない。\n\n彼はmewonen.comを開いた。\n\n一本の線を描いた。それだけが彼のすべてだった。\n\nMewonenは🕳️を見た。「待っている空間。」\n\n彼は息をした。そしてもう一本線を描いた。\n\n始めることが全てだ。\n\n今すぐ始めよう。💜 mewonnen.com"
    },
    {
        "en": "3am. Can't sleep.\n\nHer phone the only light in the room.\n\nShe typed 'why do I feel so alone' into Google.\n\nFound mewonnen.com.\n\nDrew a storm. All the chaos inside her.\n\nMewonen saw 🌪️. 'Even storms run out of rain.'\n\nShe closed her eyes. When she opened them, it was morning.\n\nThe storm had passed.\n\nDraw yours. 💜 mewonnen.com",
        "ja": "午前3時。眠れない。\n\n部屋の明かりはスマホだけ。\n\n「なぜこんなに孤独なんだろう」と検索した。\n\nmewonen.comを見つけた。\n\n嵐を描いた。心の中のすべての混沌を。\n\nMewonenは🌪️を見た。「嵐もいつかは止む。」\n\n彼女は目を閉じた。開けたとき、朝だった。\n\n嵐は過ぎ去っていた。\n\nあなたも描いてみて。💜 mewonnen.com"
    },
    {
        "en": "He hadn't spoken to anyone in 3 days.\n\nNot a call. Not a text. Just silence.\n\nHe opened mewonnen.com.\n\nDrew a sun. He didn't know why.\n\nMewonen saw ☀️. 'You are shining today.'\n\nHe laughed. It was absurd. But he felt... seen.\n\nThat was enough.\n\nDraw anything. It helps. 💜 mewonnen.com",
        "ja": "彼は3日間誰とも話さなかった。\n\n電話もメッセージもない。ただの沈黙。\n\n彼はmewonen.comを開いた。\n\n太陽を描いた。理由はわからない。\n\nMewonenは☀️を見た。「今日は輝いている。」\n\n彼は笑った。ばかげていた。でも…見てもらえた気がした。\n\nそれで十分だった。\n\n何でも描いてみて。助けになるから。💜 mewonnen.com"
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
            json={"text": text, "voice_settings": {"stability": 0.55, "similarity_boost": 0.75, "speed": 0.85}},
            timeout=30
        )
        if r.status_code == 200:
            p = "/tmp/audio.mp3"
            with open(p, "wb") as f: f.write(r.content)
            return p
    except: pass
    return None

def get_bg_image():
    queries = ["loneliness", "alone hope", "sunrise window", "rainy window", "empty room light"]
    q = random.choice(queries)
    try:
        r = requests.get(f"https://api.unsplash.com/photos/random?query={q}&orientation=portrait&client_id={UNSPLASH_KEY}", timeout=10)
        if r.status_code == 200:
            img_url = r.json()["urls"]["regular"]
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
    msg("🎬 Reel Story - Starting...")
    
    t = random.choice(STORIES)
    en_script = t["en"]
    ja_script = t["ja"]
    
    en_audio = voice(en_script)
    if not en_audio: msg("Voice failed"); return
    
    bg = get_bg_image()
    en_video = make_video(en_audio, bg)
    if not en_video: msg("Video failed"); return
    
    cap_en = f"🧠 A short story about loneliness.\n\nYou're not alone.\n\n✍️ Draw how you feel: mewonnen.com 💜\n\n#Mewonen #Loneliness #Story #MentalHealth #Reel"
    send_vid(en_video, cap_en)
    
    ja_audio = voice(ja_script)
    if ja_audio:
        ja_video = make_video(ja_audio, bg)
        if ja_video:
            cap_ja = f"🧠 孤独についての短い物語。\n\nあなたは一人じゃない。\n\n✍️ 気持ちを描いて：mewonen.com 💜\n\n#Mewonen #孤独 #物語 #メンタルヘルス"
            send_vid(ja_video, cap_ja)
    
    msg("✅ Reel posted!")

if __name__ == "__main__":
    main()
