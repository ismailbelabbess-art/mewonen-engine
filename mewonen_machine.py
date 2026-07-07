import os, random, requests
from moviepy import *

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("MEWONEN_VOICE_ID", "")
PIXABAY_KEY = os.environ.get("PIXABAY_KEY", "")
MEWONEN_TOKEN = os.environ.get("MEWONEN_TELEGRAM_BOT_TOKEN", "")
MEWONEN_CHAT = os.environ.get("MEWONEN_TELEGRAM_CHAT_ID", "")
CALM_TOKEN = os.environ.get("CALM_TELEGRAM_BOT_TOKEN", "")
CALM_CHAT = os.environ.get("CALM_TELEGRAM_CHAT_ID", "")
SAMURAI_TOKEN = os.environ.get("SAMURAI_TELEGRAM_BOT_TOKEN", "")
SAMURAI_CHAT = os.environ.get("SAMURAI_TELEGRAM_CHAT_ID", "")

TEMPLATES = [
    {
        "en": "Today I checked my bank account.\n\nThe number stared back at me. No emotion. Just nothing.\n\nMoney is just numbers on a screen. But those numbers control my life.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、銀行口座を確認した。\n\n数字が私を見つめ返した。感情はない。ただ、何もない。\n\nお金はただの画面上の数字。でもその数字が私の人生を支配している。\n\nまた明日。\n\n...\n\nたぶんね。",
        "bg": "city night"
    },
    {
        "en": "Today I tried to talk to someone.\n\nI said hello. They looked at their phone. I became invisible.\n\nWe're more connected than ever. And more alone than ever.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、誰かと話そうとした。\n\nこんにちはと言った。相手はスマホを見た。私は透明になった。\n\n私たちはかつてないほど繋がっている。そして、かつてないほど孤独だ。\n\nまた明日。\n\n...\n\nたぶんね。",
        "bg": "coffee shop"
    },
    {
        "en": "Today I read the news again.\n\nEverything is burning. Everything is dying. Here's a funny cat.\n\nThe world is heavy. But I keep carrying it.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、またニュースを読んだ。\n\nすべてが燃えている。すべてが死んでいる。面白い猫の動画。\n\n世界は重い。でも私は運び続ける。\n\nまた明日。\n\n...\n\nたぶんね。",
        "bg": "city night"
    },
    {
        "en": "Today I stepped outside.\n\nThe heat hit me like a wall. The sun doesn't care about my plans.\n\nNature doesn't judge. It just is.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、外に出た。\n\n暑さが壁のように襲ってきた。太陽は私の予定を気にしない。\n\n自然は判断しない。ただ、そこにあるだけ。\n\nまた明日。\n\n...\n\nたぶんね。",
        "bg": "sunset sky"
    },
    {
        "en": "Today I couldn't sleep again.\n\nMy brain replayed every mistake. Every embarrassing moment. Every what-if.\n\nTomorrow I'll be tired. But I'll try again.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、また眠れなかった。\n\n脳がすべての失敗を再生した。恥ずかしい瞬間。もしもの話。\n\n明日は疲れているだろう。でもまた挑戦する。\n\nまた明日。\n\n...\n\nたぶんね。",
        "bg": "night sky"
    },
    {
        "en": "Today I tried to find love.\n\nSwipe. Swipe. Swipe. Hope. Disappointment. Repeat.\n\nMaybe love isn't an algorithm. Maybe it's just time.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、愛を探そうとした。\n\nスワイプ。スワイプ。スワイプ。期待。失望。繰り返し。\n\n愛はアルゴリズムじゃないのかもしれない。たぶん、ただの時間。\n\nまた明日。\n\n...\n\nたぶんね。",
        "bg": "coffee shop"
    },
    {
        "en": "Today I called my mom.\n\nHer voice. That warmth. She asked if I'm okay. I said yes. I lied.\n\nNo matter how old I get, her voice makes me feel safe.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、母に電話した。\n\n彼女の声。その温かさ。大丈夫かと聞かれた。はいと答えた。嘘をついた。\n\nいくつになっても、母の声は私を安心させる。\n\nまた明日。\n\n...\n\nたぶんね。",
        "bg": "quiet morning"
    },
    {
        "en": "Today I went to work.\n\nSitting. Staring. Typing. Pretending to care.\n\nI work to live. But sometimes I forget to live.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、仕事に行った。\n\n座って。見つめて。タイピング。関心があるふり。\n\n生きるために働く。でも時々、生きることを忘れる。\n\nまた明日。\n\n...\n\nたぶんね。",
        "bg": "city night"
    },
    {
        "en": "Today I tried to take care of myself.\n\nI drank water. I stretched. I breathed.\n\nBut I tried. That counts. Right?\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、自分を大切にしようとした。\n\n水を飲んだ。ストレッチした。呼吸した。\n\nでも挑戦した。それで十分。そうでしょ？\n\nまた明日。\n\n...\n\nたぶんね。",
        "bg": "quiet morning"
    },
    {
        "en": "Today I checked my phone 47 times.\n\nNothing important. Just habit. Just emptiness.\n\nOne day, I'll learn to just be.\n\nSee you tomorrow.\n\n...\n\nMaybe.",
        "ja": "今日、47回スマホをチェックした。\n\n何も重要じゃない。ただの習慣。ただの空虚。\n\nいつか、ただ存在することを学ぶだろう。\n\nまた明日。\n\n...\n\nたぶんね。",
        "bg": "empty street"
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

def bg_video(query):
    try:
        r = requests.get(f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q={query}&per_page=5&orientation=vertical", timeout=10)
        hits = r.json().get("hits", [])
        if not hits: return None
        v = random.choice(hits).get("videos", {})
        for s in ["large", "medium", "small", "tiny"]:
            if s in v:
                r2 = requests.get(v[s]["url"], timeout=30)
                p = "/tmp/bg.mp4"
                with open(p, "wb") as f: f.write(r2.content)
                return p
    except: pass
    return None

def make_video(audio_path, bg_path):
    try:
        a = AudioFileClip(audio_path)
        dur = a.duration + 3
        if bg_path:
            v = VideoFileClip(bg_path)
            if v.duration < dur:
                repeats = int(dur / v.duration) + 1
                clips = [v] * repeats
                v = concatenate_videoclips(clips).with_duration(dur)
            else:
                v = v.with_duration(dur)
            v = v.resized(height=1920)
            if v.w > 1080: v = v.cropped(x_center=v.w/2, width=1080)
            if v.w < 1080: v = v.resized(width=1080)
        else:
            v = ColorClip(size=(1080, 1920), color=(10, 10, 24), duration=dur)
        v = v.with_audio(a)
        out = "/tmp/video.mp4"
        v.write_videofile(out, codec='libx264', audio_codec='aac', fps=24, preset='ultrafast', threads=2, logger=None)
        v.close(); a.close()
        return out
    except Exception as e:
        print(f"Video error: {e}")
        return None

def main():
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, "🎬 Mewonen Engine - Starting...")
    
    t = random.choice(TEMPLATES)
    en_script = t["en"]
    ja_script = t["ja"]
    bg_query = t["bg"]
    
    en_audio = voice(en_script)
    if not en_audio:
        msg(MEWONEN_TOKEN, MEWONEN_CHAT, "Voice failed")
        return
    
    bg = bg_video(bg_query)
    en_video = make_video(en_audio, bg)
    if not en_video:
        msg(MEWONEN_TOKEN, MEWONEN_CHAT, "Video failed")
        return
    
    cap_en = f"✍️ Draw your mood today\n\n💜 mewonnen.com\n\n{en_script.split(chr(10))[2]}\n\n#mewonen #relatable #feelings #viral #fyp"
    send_vid(MEWONEN_TOKEN, MEWONEN_CHAT, en_video, cap_en)
    if CALM_TOKEN and CALM_CHAT:
        send_vid(CALM_TOKEN, CALM_CHAT, en_video, cap_en)
    
    ja_audio = voice(ja_script)
    if ja_audio:
        ja_video = make_video(ja_audio, bg)
        if ja_video:
            cap_ja = f"✍️ 今日の気持ちを描こう\n\n💜 mewonnen.com\n\n{ja_script.split(chr(10))[2]}\n\n#mewonen #気持ち #メンタルヘルス #viral"
            if SAMURAI_TOKEN and SAMURAI_CHAT:
                send_vid(SAMURAI_TOKEN, SAMURAI_CHAT, ja_video, cap_ja)
    
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, f"✅ Posted!\n\n{en_script[:150]}...")

if __name__ == "__main__":
    main()
