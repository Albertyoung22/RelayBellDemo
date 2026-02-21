# -*- coding: utf-8 -*-
import os, secrets, asyncio, io
from flask import Flask, request, jsonify, send_file, redirect, send_from_directory

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# 自動偵測絕對路徑
ROOT = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(ROOT, 'static', 'ui')

# --- 核心導覽 ---

@app.route('/')
def home():
    # 預設進入展示專區
    return redirect("/demo")

@app.route('/demo')
def demo():
    # 直接抓取展示專用的 demo.html
    return send_from_directory(UI_DIR, 'demo.html')

# 讓 /login 變成一個自動植入登入憑證的頁面
@app.route('/login')
def login_page():
    return f'''
    <html><body style="font-family:sans-serif; text-align:center; padding-top:100px; background:#f0f2f5;">
    <div style="background:white; display:inline-block; padding:40px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
        <h2 style="color:#333;">RelayBell 展示模式</h2>
        <p style="color:#666;">點擊下方按鈕即可繞過密碼檢查</p>
        <button onclick="localStorage.setItem('X_TOKEN', 'demo-token'); location.href='/static/ui/index.html';" 
        style="padding:15px 30px; font-size:18px; background:#1e7bd8; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">
        🚀 一鍵登入並進入主控台
        </button>
        <div style="margin-top:25px;"><a href="/demo" style="color:#7c4dff; text-decoration:none;">或是直接前往 AI 展示廳 ✨</a></div>
    </div>
    </body></html>
    '''

# 劫持所有 /static/ui/ 檔案，解決路徑問題
@app.route('/static/ui/<path:filename>')
def serve_ui(filename):
    return send_from_directory(UI_DIR, filename)

# --- 模擬原本系統 API (預防 index.html 出現錯誤彈窗) ---

@app.route('/state')
def state():
    return jsonify({
        "playing": "Demo Live", 
        "progress": 0, 
        "volume": 80,
        "muted": False,
        "lang": "zh-TW", 
        "gender": "female",
        "rate": "0%",
        "edge_tts_status": "OK",
        "ngrok_url": "Showcase Mode"
    })

@app.route('/timetable')
@app.route('/files')
def fake_api():
    return jsonify(ok=True, files=[], data={"items":[]})

# --- AI 展示專用 API ---

@app.route('/api/translate', methods=['POST'])
def translate():
    from deep_translator import GoogleTranslator
    try:
        d = request.json or {}
        # 自動偵測來源並翻譯為目標語言
        t = GoogleTranslator(source='auto', target=d.get('target', 'zh-TW')).translate(d.get('text', ''))
        return jsonify(ok=True, translated=t)
    except Exception as e: return jsonify(ok=False, error=str(e)), 500

@app.route('/api/tts_preview', methods=['POST'])
def tts():
    import edge_tts
    try:
        d = request.json or {}
        text = d.get('text', '')
        voice = d.get('lang', 'zh-TW-HsiaoChenNeural')
        
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
    # Render 會抓取 PORT 環境變數（通常是 10000）
    p = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=p)
