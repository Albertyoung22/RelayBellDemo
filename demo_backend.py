# -*- coding: utf-8 -*-
import os
import secrets
import asyncio
import io
from flask import Flask, request, jsonify, render_template, send_file, redirect, send_from_directory
import edge_tts
from deep_translator import GoogleTranslator

# 自動偵測正確的基底路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UI_DIR = os.path.join(STATIC_DIR, 'ui')

app = Flask(__name__, static_folder=STATIC_DIR)
app.secret_key = secrets.token_hex(16)

# 語音對照表
VOICE_ID_TABLE = {
    "zh-TW": {"female": "zh-TW-HsiaoChenNeural", "male": "zh-TW-YunJheNeural"},
    "en-US": {"female": "en-US-AriaNeural", "male": "en-US-GuyNeural"},
    "ja-JP": {"female": "ja-JP-NanamiNeural", "male": "ja-JP-KeitaNeural"},
    "ko-KR": {"female": "ko-KR-SunHiNeural", "male": "ko-KR-InJoonNeural"},
}

# --- 路由 ---

@app.route('/')
def index():
    # 強制檢查檔案是否存在並導向
    return redirect("/static/ui/index.html")

# 解決 Render 上 static/ui 路徑遺失的問題
@app.route('/static/ui/<path:filename>')
def serve_ui(filename):
    return send_from_directory(UI_DIR, filename)

@app.route('/demo')
def demo_page():
    # 直接在 ui 目錄尋找 demo.html
    return send_from_directory(UI_DIR, 'demo.html')

@app.route('/api/translate', methods=['POST'])
def api_translate():
    try:
        data = request.json or request.form
        text = data.get('text')
        target = data.get('target', 'zh-TW')
        source = data.get('source', 'auto')
        if not text: return jsonify(ok=False, error="Missing text"), 400
        translated = GoogleTranslator(source=source, target=target).translate(text)
        return jsonify(ok=True, translated=translated)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@app.route('/api/tts_preview', methods=['POST'])
def api_tts_preview():
    try:
        data = request.json or {}
        text = data.get('text')
        lang = data.get('lang')
        gender = data.get('gender', 'female')
        if not text: return jsonify(ok=False, error="No text"), 400
        
        # 決定聲音 ID (支援直接 ID 或語言代碼轉換)
        voice = lang if "-Neural" in str(lang) else VOICE_ID_TABLE.get(lang, VOICE_ID_TABLE["zh-TW"]).get(gender, "zh-TW-HsiaoChenNeural")
        
        async def _gen():
            communicate = edge_tts.Communicate(text, voice)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio": audio_data += chunk["data"]
            return audio_data

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            audio_bytes = loop.run_until_complete(_gen())
        finally:
            loop.close()
            
        return send_file(io.BytesIO(audio_bytes), mimetype="audio/mpeg", download_name="preview.mp3")
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

if __name__ == "__main__":
    # Render 會給 PORT 環境變數，沒給則預設 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
