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
    {"h": "checked my bank account", "b": ["The number stared back at me. No emotion. Just... nothing.", "I closed the app. Opened it again. Still nothing."], "p": "Money is just numbers on a screen. But those numbers control my life.", "bg": "city night"},
    {"h": "tried to talk to someone today", "b": ["I said hello. They looked at their phone. I became invisible.", "200 friends online. Zero in real life."], "p": "We're more connected than ever. And more alone than ever.", "bg": "coffee shop"},
    {"h": "read the news again", "b": ["Everything is burning. Everything is dying. Here's a funny cat.", "I don't know how to feel anymore. So I scroll."], "p": "The world is heavy. But I keep carrying it.", "bg": "city night"},
    {"h": "stepped outside", "b": ["The heat hit me like a wall. The sun doesn't care about my plans.", "A bird looked at me. I think it knew I was struggling."], "p": "Nature doesn't judge. It just... is.", "bg": "sunset sky"},
    {"h": "couldn't sleep again", "b": ["My brain decided to replay every mistake. Every embarrassing moment. Every what-if.", "3am. The world is asleep. I'm here. With my thoughts."], "p": "Tomorrow I'll be tired. But I'll try again.", "bg": "night sky"},
    {"h": "tried to find love", "b": ["Swipe. Swipe. Swipe. Hope. Disappointment. Repeat.", "Someone asked what I do for fun. I said 'survive.' They unmatched."], "p": "Maybe love isn't an algorithm. Maybe it's just... time.", "bg": "coffee shop"},
    {"h": "called my mom", "b": ["Her voice. That warmth. She asked if I'm okay. I said yes. I lied.", "She knew. Moms always know."], "p": "No matter how old I get, her voice makes me feel... safe.", "bg": "quiet morning"},
    {"h": "went to work", "b": ["Sitting. Staring. Typing. Pretending to care.", "My boss said 'great job.' I did nothing. Nothing matters."], "p": "I work to live. But sometimes I forget to live.", "bg": "city night"},
    {"h": "tried to take care of myself", "b": ["I drank water. I stretched. I breathed.", "It's hard. Being kind to yourself. Harder than it should be."], "p": "But I tried. That counts. Right?", "bg": "quiet morning"},
    {"h": "checked my phone 47 times today", "b": ["Nothing important. Just habit. Just... emptiness.", "I put it down. Picked it up. Put it down again."], "p": "One day, I'll learn to just... be.", "bg": "empty street"}
]

# Traductions japonaises (pré-faites pour éviter API traduction)
JA_TRANSLATIONS = {
    "checked my bank account": "銀行口座を確認した",
    "tried to talk to someone today": "今日誰かと話そうとした",
    "read the news again": "またニュースを読んだ",
    "stepped outside": "外に出た",
    "couldn't sleep again": "また眠れなかった",
    "tried to find love": "愛を探そうとした",
    "called my mom": "母に電話した",
    "went to work": "仕事に行った",
    "tried to take care of myself": "自分を大切にしようとした",
    "checked my phone 47 times today": "今日47回スマホをチェックした",
    "The number stared back at me. No emotion. Just... nothing.": "数字が私を見つめ返した。感情はない。ただ...何もない。",
    "I closed the app. Opened it again. Still nothing.": "アプリを閉じた。また開いた。まだ何もない。",
    "I said hello. They looked at their phone. I became invisible.": "こんにちはと言った。相手はスマホを見た。私は透明になった。",
    "200 friends online. Zero in real life.": "オンラインに200人の友達。現実にはゼロ。",
    "Everything is burning. Everything is dying. Here's a funny cat.": "すべてが燃えている。すべてが死んでいる。面白い猫の動画。",
    "I don't know how to feel anymore. So I scroll.": "もうどう感じていいかわからない。だからスクロールする。",
    "The heat hit me like a wall. The sun doesn't care about my plans.": "暑さが壁のように襲ってきた。太陽は私の予定を気にしない。",
    "A bird looked at me. I think it knew I was struggling.": "鳥が私を見た。私が苦しんでいるのを知っていたと思う。",
    "My brain decided to replay every mistake. Every embarrassing moment. Every what-if.": "脳がすべての失敗を再生し始めた。恥ずかしい瞬間。もしもの話。",
    "3am. The world is asleep. I'm here. With my thoughts.": "午前3時。世界は眠っている。私はここにいる。考え事と一緒に。",
    "Swipe. Swipe. Swipe. Hope. Disappointment. Repeat.": "スワイプ。スワイプ。スワイプ。期待。失望。繰り返し。",
    "Someone asked what I do for fun. I said 'survive.' They unmatched.": "趣味は何かと聞かれた。「生き残ること」と答えた。マッチ解除された。",
    "Her voice. That warmth. She asked if I'm okay. I said yes. I lied.": "彼女の声。その温かさ。大丈夫かと聞かれた。はいと答えた。嘘をついた。",
    "She knew. Moms always know.": "彼女は知っていた。母親はいつも知っている。",
    "Sitting. Staring. Typing. Pretending to care.": "座って。見つめて。タイピング。関心があるふり。",
    "My boss said 'great job.' I did nothing. Nothing matters.": "上司は「よくやった」と言った。私は何もしなかった。何も重要じゃない。",
    "I drank water. I stretched. I breathed.": "水を飲んだ。ストレッチした。呼吸した。",
    "It's hard. Being kind to yourself. Harder than it should be.": "難しい。自分に優しくすること。思ったよりずっと難しい。",
    "Nothing important. Just habit. Just... emptiness.": "何も重要じゃない。ただの習慣。ただの...空虚。",
    "I put it down. Picked it up. Put it down again.": "置いた。また手に取った。また置いた。",
    "Money is just numbers on a screen. But those numbers control my life.": "お金はただの画面上の数字。でもその数字が私の人生を支配している。",
    "We're more connected than ever. And more alone than ever.": "私たちはかつてないほどつながっている。そしてかつてないほど孤独だ。",
    "The world is heavy. But I keep carrying it.": "世界は重い。でも私は運び続ける。",
    "Nature doesn't judge. It just... is.": "自然は判断しない。ただ...そこにある。",
    "Tomorrow I'll be tired. But I'll try again.": "明日は疲れているだろう。でもまた挑戦する。",
    "Maybe love isn't an algorithm. Maybe it's just... time.": "愛はアルゴリズムじゃないのかもしれない。たぶん...時間だけ。",
    "No matter how old I get, her voice makes me feel... safe.": "いくつになっても、彼女の声は私を...安心させる。",
    "I work to live. But sometimes I forget to live.": "生きるために働く。でも時々生きることを忘れる。",
    "But I tried. That counts. Right?": "でも挑戦した。それで十分。そうでしょ？",
    "One day, I'll learn to just... be.": "いつか、ただ...存在することを学ぶだろう。",
    "See you tomorrow.": "また明日。",
    "Maybe.": "たぶんね。",
    "Today I": "今日、私は"
}

def msg(token, chat, text):
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat, "text": text}, timeout=10)
    except: pass

def send_vid(token, chat, path, caption):
    try:
        with open(path, "rb") as f:
            requests.post(f"https://api.telegram.org/bot{token}/sendVideo", data={"chat_id": chat, "caption": caption}, files={"video": f}, timeout=60)
        return True
    except: return False

def script():
    t = random.choice(TEMPLATES)
    b = random.choice(t["b"])
    en = f"Today I {t['h']}.\n\n{b}\n\n{t['p']}\n\nSee you tomorrow.\n\n...\n\nMaybe."
    # Version japonaise
    ja_h = JA_TRANSLATIONS.get(t['h'], t['h'])
    ja_b = JA_TRANSLATIONS.get(b, b)
    ja_p = JA_TRANSLATIONS.get(t['p'], t['p'])
    ja = f"今日、私は{ja_h}。\n\n{ja_b}\n\n{ja_p}\n\nまた明日。\n\n...\n\nたぶんね。"
    return t, en, ja

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
    
    t, en_script, ja_script = script()
    
    # Version anglaise
    en_audio = voice(en_script)
    if not en_audio:
        msg(MEWONEN_TOKEN, MEWONEN_CHAT, "Voice failed")
        return
    
    bg = bg_video(t["bg"])
    en_video = make_video(en_audio, bg)
    if not en_video:
        msg(MEWONEN_TOKEN, MEWONEN_CHAT, "Video failed")
        return
    
    cap_en = f"M E W O N E N\n\n{en_script.split(chr(10))[1]}\n\n💜 mewonnen.com\n\n#mewonen #relatable #feelings #viral"
    
    # Poster sur Mewonen
    send_vid(MEWONEN_TOKEN, MEWONEN_CHAT, en_video, cap_en)
    # Poster sur Calm Chaos
    if CALM_TOKEN and CALM_CHAT:
        send_vid(CALM_TOKEN, CALM_CHAT, en_video, cap_en)
    
    # Version japonaise
    ja_audio = voice(ja_script)
    if ja_audio:
        ja_video = make_video(ja_audio, bg)
        if ja_video:
            cap_ja = f"M E W O N E N\n\n{ja_script.split(chr(10))[1]}\n\n💜 mewonnen.com\n\n#mewonen #気持ち #メンタルヘルス"
            if SAMURAI_TOKEN and SAMURAI_CHAT:
                send_vid(SAMURAI_TOKEN, SAMURAI_CHAT, ja_video, cap_ja)
    
    msg(MEWONEN_TOKEN, MEWONEN_CHAT, f"✅ Posted!\n\n{en_script[:150]}...")

if __name__ == "__main__":
    main()
