@echo off
chcp 65001
echo 正在下載 Piper 語音模型 (zh_CN-huayan-medium)...
echo 下載 .onnx 模型...
curl -L -o zh_CN-huayan-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/main/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx
echo.
echo 下載 .json 設定檔...
curl -L -o zh_CN-huayan-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/main/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx.json
echo.
echo 下載完成!
echo 現在您可以執行 piper_standalone.py 了。
pause
