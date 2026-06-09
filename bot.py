import os
import requests
import google.generativeai as genai
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Điền thông tin của bạn vào đây
GEMINI_API_KEY = "ĐIỀN_GEMINI_API_KEY_CỦA_BẠN"
OA_ACCESS_TOKEN = "ĐIỀN_OA_ACCESS_TOKEN_CỦA_BẠN"

genai.configure(api_key=GEMINI_API_KEY)

@app.get("/webhook")
async def verify_webhook(request: Request):
    return JSONResponse({"status": "ok"})

@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    
    try:
        event = data.get("event_name", "")
        
        # Chỉ xử lý khi có ảnh gửi vào nhóm
        if event != "g_send_image":
            return JSONResponse({"status": "ignored"})
        
        msg = data.get("message", {})
        image_url = msg.get("attachments", [{}])[0].get("payload", {}).get("url", "")
        group_id = data.get("recipient", {}).get("id", "")
        
        if not image_url or not group_id:
            return JSONResponse({"status": "no image"})
        
        # Tải ảnh về
        img_data = requests.get(image_url).content
        
        # Gửi sang Gemini Vision đọc số
        model = genai.GenerativeModel("gemini-2.5-flash")
        import PIL.Image, io
        image = PIL.Image.open(io.BytesIO(img_data))
        
        prompt = """Đây là ảnh container hoặc seal/chì niêm phong.
Hãy đọc và trích xuất:
1. Số container (format: 4 chữ cái + 7 số, ví dụ: TCKU3456789)
2. Số chì/seal (dãy số trên dây chì niêm phong)

Trả lời đúng format:
Container: [số container]
Chì: [số chì]

Nếu không đọc được thì ghi: Không đọc được - ảnh mờ hoặc không đúng góc chụp"""
        
        response = model.generate_content([prompt, image])
        result_text = response.text
        
        # Reply vào nhóm Zalo
        reply_url = "https://openapi.zalo.me/v3.0/oa/message/cs"
        headers = {
            "access_token": OA_ACCESS_TOKEN,
            "Content-Type": "application/json"
        }
        payload = {
            "recipient": {"id": group_id},
            "message": {"text": f"🤖 BN CHAIN BOT\n{result_text}"}
        }
        requests.post(reply_url, json=payload, headers=headers)
        
    except Exception as e:
        print(f"Lỗi: {e}")
    
    return JSONResponse({"status": "ok"})