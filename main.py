from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yt_dlp
import os
import uuid

app = FastAPI()

# तपाईंको Netlify वेबसाइटबाट आउने अनुरोधलाई अनुमति दिन (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"status": "ClipForge YouTube Backend is Running!"}

@app.get("/fetch-video")
def fetch_video(url: str):
    if not url or ("youtube.com" not in url and "youtu.be" not in url):
        raise HTTPException(status_code=400, detail="मान्य YouTube लिंक हाल्नुहोस्।")

    # पुरानो फाइल सफा गर्ने (सर्भर भरिन नदिन)
    for f in os.listdir(DOWNLOAD_DIR):
        try:
            os.remove(os.path.join(DOWNLOAD_DIR, f))
        except Exception:
            pass

    file_id = str(uuid.uuid4())[:8]
    output_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp4")

    # १०८०p सम्मको MP4 भिडियो तान्ने सेटिङ
    ydl_opts = {
        'format': 'best[ext=mp4][height<=1080]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="भिडियो डाउनलोड हुन सकेन।")

        return FileResponse(
            output_path, 
            media_type="video/mp4", 
            filename=f"clipforge_{file_id}.mp4"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YouTube Error: {str(e)}")
