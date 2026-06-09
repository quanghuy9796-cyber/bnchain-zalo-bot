import os
import requests
import google.generativeai as genai
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import PIL.Image
import io

app = FastAPI()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OA_ACCESS_TOKEN = os.environ.get("OA_ACCESS_TOKEN", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

@app.get("/")
async def root():
    return JSONResponse({"status": "BN CHAIN BOT running"})

@app.get("/zalo_verifierGeQV9QEF2WrRYhi2lVWtLKsEX5wX-548EJCs.html")
async def zalo_verify():
    return HTMLResponse("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta property="zalo-platform-site-verification" content="GeQV9QEF2WrRYhi2lVWtLKsEX5wX-548EJCs" />
</head>
<body>
There Is No Limit To What You Can Accomplish Using Zalo!
</body>
</html>""")

@app.get("/webhook")
async def verify_webhook(request: Request):
    return JSONResponse({"status": "ok"})

@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    try:
        event = data.get("event_name", "")
        if event != "g_send_image":
            return JSONResponse({"status": "ignored"})

        msg = data.get("message", {})
        attachments = msg.get("attachments", [])
        if not attachments:
            return JSONResponse({"status": "no attachment"})

        image_url = attachments[0].get("payload", {}).get("url", "")
        group_id = data.get("recipient", {}).get("id", "")

        if not image_url or not group_id:
            return JSONResponse({"status": "missing data"})

        img_data = requests.get(image_url).content
        model = genai.GenerativeModel("gemini-2.5-flash")
        image = PIL.Image.open(io.BytesIO(img_data))

        prompt = """Đây là ảnh container hoặc seal/chì niêm phong.
Hãy đọc và trích xuất:
1. Số container (format: 4 chữ cái + 7 số, ví dụ: TCKU3456789)
2. Số chì/seal (dãy số trên dây chì niêm phong)
3. Thời gian nếu có trên ảnh
4. Vị trí nếu có trên ảnh

Trả lời đúng format:
Container: [số container]
Chì: [số chì]
Thời gian: [nếu có]
Vị trí: [nếu có]

Nếu không đọc được thì ghi: Không đọc được - ảnh mờ hoặc không đúng góc chụp"""

        response = model.generate_content([prompt, image])
        result_text = response.text

        reply_url = "https://openapi.zalo.me/v3.0/oa/message/cs"
        headers = {
            "access_token": OA_ACCESS_TOKEN,
            "Content-Type": "application/json"
        }
        payload = {
            "recipient": {"id": group_id},
            "message": {"text": f"BN CHAIN BOT\n{result_text}"}
        }
        requests.post(reply_url, json=payload, headers=headers)

    except Exception as e:
        print(f"Loi: {e}")

    return JSONResponse({"status": "ok"})
