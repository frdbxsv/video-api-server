from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp
import os

app = FastAPI()

# --- RENDER LİNKİN (Dəyişmə) ---
TUNNEL_URL = "https://video-api-server-9b5n.onrender.com"

class VideoRequest(BaseModel):
    url: str

@app.post("/download")
def download_video(request: VideoRequest):
    print(f"Video yüklənir: {request.url}")
    
    output_filename = "video.mp4"
    
    if os.path.exists(output_filename):
        os.remove(output_filename)

    # --- YENİLİK: Instagramı aldatmaq üçün parametrlər ---
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_filename,
        'quiet': True,
        'no_warnings': True,
        # Instagram üçün vacib olan "Maska" (User Agent)
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        # Xəta olsa dayanmasın, davam etsin
        'ignoreerrors': True, 
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=True)
            
            # Instagram bəzən 'entries' qaytarır (bir neçə video olanda)
            if 'entries' in info:
                info = info['entries'][0]

            local_video_link = f"{TUNNEL_URL}/get_video"
            
            return {
                "status": "success",
                "title": info.get('title', 'Instagram Video'),
                "video_url": local_video_link,
                "thumbnail": info.get('thumbnail', '')
            }
    except Exception as e:
        print(f"Xəta: {e}")
        return {"status": "error", "message": "Instagram bu videonu blokladı və ya giriş tələb olunur."}

@app.get("/get_video")
def get_video_file():
    file_path = "video.mp4"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4", filename="yuklenen_video.mp4")
    else:
        return {"error": "Fayl tapılmadı"}
