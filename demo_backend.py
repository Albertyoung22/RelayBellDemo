# -*- coding: utf-8 -*-
import os, secrets, asyncio, io
from flask import Flask, request, jsonify, send_file, redirect, send_from_directory

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

ROOT = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(ROOT, 'static', 'ui')

# --- 核心導覽 ---

@app.route('/')
def home():
    return redirect("/static/ui/index.html")

@app.route('/demo')
def demo():
    return send_from_directory(UI_DIR, 'demo.html')

@app.route('/login')
def login_page():
    return f'''
    <html><body style="font-family:sans-serif; text-align:center; padding-top:100px; background:#f0f2f5;">
    <div style="background:white; display:inline-block; padding:40px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
        <h2>RelayBell 展示模式</h2>
        <button onclick="localStorage.setItem('X_TOKEN', 'demo-token'); location.href='/static/ui/index.html';" 
        style="padding:15px 30px; font-size:18px; background:#1e7bd8; color:white; border:none; border-radius:8px; cursor:pointer;">
        🚀 一鍵登入並進入主控台
        </button>
        <div style="margin-top:20px;"><a href="/demo">或是 前往 AI 展示廳 ✨</a></div>
    </div>
    </body></html>
    '''

@app.route('/static/ui/<path:filename>')
def serve_ui(filename):
    return send_from_directory(UI_DIR, filename)

@app.route('/download/<path:filename>')
def download_file(filename):
    # 先在 UI 目錄找，找不到再去根目錄，這裏簡單處理
    for d in [UI_DIR, ROOT]:
        p = os.path.join(d, filename)
        if os.path.exists(p):
            return send_from_directory(d, filename)
    return "File not found", 404

# --- 模擬原本系統 API ---

@app.route('/state')
def state():
    return jsonify({
        "playing": "Frontend Playback Mode", 
        "progress": 0, 
        "volume": 80,
        "muted": False,
        "lang": "zh-TW", 
        "gender": "female",
        "rate": "0%",
        "edge_tts_status": "OK",
        "ngrok_url": "Demo Mode",
        "relay_auto": False,
        "chime_enabled": True
    })

@app.route('/api/get_relay_config')
@app.route('/api/get_chime_config')
@app.route('/timetable')
@app.route('/files')
def fake_get_apis():
    return jsonify(ok=True, files=[], data={"items":[]}, enabled=True, auto_on=False)

@app.route('/taigi/translate', methods=['POST'])
def taigi_trans():
    d = request.json or {}
    text = d.get('text', '')
    return jsonify(ok=True, text="[台語模擬] " + text)

@app.route('/taigi/say', methods=['POST'])
def taigi_say():
    # 模擬台語播放，回傳一個展示用的連結
    return jsonify(ok=True, file="demo_taigi.mp3", url="/api/tts_preview")

@app.route('/sendmp3', methods=['POST'])
def send_mp3():
    return jsonify(ok=True, message="MP3 Command Received", filename="demo.mp3")

@app.route('/cmd', methods=['POST'])
@app.route('/api/speak_v2', methods=['POST'])
@app.route('/api/speak_audio_blob', methods=['POST'])
@app.route('/api/set_relay_config', methods=['POST'])
@app.route('/api/set_chime_config', methods=['POST'])
@app.route('/setvol', methods=['POST'])
@app.route('/setrate', methods=['POST'])
@app.route('/autounmute', methods=['POST'])
@app.route('/upload', methods=['POST'])
@app.route('/delete', methods=['POST'])
def fake_post_apis():
    return jsonify(ok=True, message="Demo mode: command simulated")

# --- AI 展示功能 API ---

@app.route('/translate', methods=['POST'])
@app.route('/api/translate', methods=['POST'])
def translate():
    from deep_translator import GoogleTranslator
    try:
        d = request.json or request.form or {}
        text = d.get('text')
        target = d.get('target', 'zh-TW')
        source = d.get('source', 'auto')
        if not text: return jsonify(ok=False, error="No text"), 400
        t = GoogleTranslator(source=source, target=target).translate(text)
        return jsonify(ok=True, translated=t, translatedText=t)
    except Exception as e: return jsonify(ok=False, error=str(e)), 500

@app.route('/api/tts_preview', methods=['POST'])
def tts():
    import edge_tts
    try:
        d = request.json or {}
        text = d.get('text', '這是測試語音')
        lang = d.get('lang', 'zh-TW-HsiaoChenNeural')
        lang_map = {
            'zh': 'zh-TW-HsiaoChenNeural', 'zh-TW': 'zh-TW-HsiaoChenNeural',
            'en': 'en-US-AriaNeural', 'en-US': 'en-US-AriaNeural',
            'ja': 'ja-JP-NanamiNeural', 'ko': 'ko-KR-SunHiNeural',
            'nan': 'zh-TW-YunJheNeural', 'nan-TW': 'zh-TW-YunJheNeural'
        }
        voice = lang if "-Neural" in str(lang) else lang_map.get(lang, "zh-TW-HsiaoChenNeural")
        
        async def _gen():
            tts = edge_tts.Communicate(text, voice)
            o = io.BytesIO()
            async for c in tts.stream():
                if c["type"] == "audio": o.write(c["data"])
            o.seek(0); return o
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            audio_io = loop.run_until_complete(_gen())
        finally:
            loop.close()
        return send_file(audio_io, mimetype="audio/mpeg")
    except Exception as e: return jsonify(ok=False, error=str(e)), 500

if __name__ == "__main__":
    p = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=p)
