import socket
import threading
import time
import xml.etree.ElementTree as ET

class CWATCPClient:
    def __init__(self, host="scseewser.cwa.gov.tw", port=14002, account="", password=""):
        self.host = host
        self.port = port
        self.account = account
        self.password = password
        self.running = False
        self.sock = None
        self.callback = None

    def start(self, callback=None):
        self.callback = callback
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.running = False
        if self.sock:
            try: self.sock.close()
            except: pass

    def _loop(self):
        while self.running:
            try:
                print(f"[TCP] Connecting to {self.host}:{self.port}...")
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(30)
                self.sock.connect((self.host, self.port))
                
                # CWA LOGIN
                login_msg = f"user:{self.account} pwd:{self.password}\r\n"
                self.sock.send(login_msg.encode('utf-8'))
                
                print("[TCP] Logged in, waiting for data...")
                
                while self.running:
                    try:
                        data = self.sock.recv(8192)
                        if not data:
                            print("[TCP] Server closed connection.")
                            break
                        self._handle_raw_data(data)
                    except socket.timeout:
                        # Keep-alive or just wait
                        continue
                    except Exception as inner_e:
                        print(f"[TCP] Receive Error: {inner_e}")
                        break
                
            except Exception as e:
                print(f"[TCP] Connection Error: {e}")
                time.sleep(10)
            finally:
                if self.sock:
                    try: 
                        self.sock.shutdown(socket.SHUT_RDWR)
                        self.sock.close()
                    except: pass
                self.sock = None

    def _handle_raw_data(self, data):
        try:
            # 這裡需要實作 CWA 的封包重組邏輯（通常 XML 會以特定字元結尾）
            text = data.decode('utf-8', errors='ignore')
            print(f"[TCP] Raw Data: {text[:100]}...")
            
            # 範例：如果 text 是完整的 XML
            if "<Earthquake" in text:
                self._parse_xml(text)
        except Exception as e:
            print(f"[TCP] Parse Error: {e}")

    def _parse_xml(self, xml_str):
        try:
            # 簡單解析範例
            root = ET.fromstring(xml_str)
            # 提取資訊並呼叫 callback
            if self.callback:
                self.callback(xml_str)
        except Exception as e:
            print(f"[TCP] XML Error: {e}")

if __name__ == "__main__":
    # 使用使用者提供的憑據進行簡單接收測試
    client = CWATCPClient(account="SS213316", password="2570382")
    client.start(lambda x: print(f"NEW QUAKE: {x[:200]}"))
    
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        client.stop()
