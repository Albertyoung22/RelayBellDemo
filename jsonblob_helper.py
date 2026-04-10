# -*- coding: utf-8 -*-
import requests
import json
import os
import sys

# [CONFIG] JsonBlob URL - 將在第一次執行時自動填入
# [CONFIG] JsonBlob URL - Will be automatically filled on first run
JSON_BLOB_URL = "https://jsonblob.com/api/jsonBlob/019d22f9-b6f5-71af-a43d-68ccf5fc59bd" 

class JsonBlobDB:
    def __init__(self, url=None):
        self.url = url or JSON_BLOB_URL
        if not self.url:
            self.init_blob()

    def init_blob(self):
        """建立新的 JsonBlob 並將網址寫回程式碼中 (Self-modifying code)"""
        print("[JsonBlob] 正在隨機建立獨一無二的遠端資料庫金鑰...")
        try:
            # 建立初始空的 Blob
            r = requests.post("https://jsonblob.com/api/jsonBlob", json={"init": True}, timeout=10)
            if r.status_code == 201:
                # 取得 Location Header (完整網址)
                loc = r.headers.get("Location")
                if not loc.startswith("http"):
                    loc = "https://jsonblob.com" + loc
                
                self.url = loc
                print(f"[JsonBlob] 建立成功！網址: {self.url}")
                
                # 自動寫死到本程式碼檔中
                self._hardcode_url(loc)
            else:
                print(f"[JsonBlob] 建立失敗: {r.status_code}")
        except Exception as e:
            print(f"[JsonBlob] 連線錯誤: {e}")

    def _hardcode_url(self, new_url):
        """將網址寫死到目前的 .py 檔案中"""
        try:
            script_path = os.path.abspath(__file__)
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 使用正規表達式或簡單取代
            old_line = 'JSON_BLOB_URL = "https://jsonblob.com/api/jsonBlob/019d22f9-b6f5-71af-a43d-68ccf5fc59bd"'
            new_line = f'JSON_BLOB_URL = "{new_url}"'
            
            if old_line in content:
                new_content = content.replace(old_line, new_line)
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"[JsonBlob] 已將網址自動備份至程式碼: {script_path}")
            else:
                print("[JsonBlob] 找不到可取代的 URL 欄位，請手動更新程式碼。")
        except Exception as e:
            print(f"[JsonBlob] 自動更新程式碼失敗: {e}")

    def push(self, data):
        """上傳 JSON 資料"""
        if not self.url: return False
        try:
            r = requests.put(self.url, json=data, timeout=10)
            return r.status_code == 200
        except: return False

    def pull(self):
        """下載 JSON 資料"""
        if not self.url: return None
        try:
            r = requests.get(self.url, timeout=10)
            return r.json()
        except: return None

# 使用範例
if __name__ == "__main__":
    db = JsonBlobDB()
    if db.url:
        print(f"目前使用的資料庫: {db.url}")
        # 測試備份
        test_data = {"last_backup": "2024-03-25", "status": "online"}
        if db.push(test_data):
            print("備份成功！")
            print("讀取回傳:", db.pull())
