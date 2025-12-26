from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp
import os

app = FastAPI()

# --- RENDER LİNKİN ---
TUNNEL_URL = "https://video-api-server-9b5n.onrender.com"

class VideoRequest(BaseModel):
    url: str

@app.post("/download")
def download_video(request: VideoRequest):
    print(f"Video yüklənir: {request.url}")
    
    output_filename = "video.mp4"
    
    if os.path.exists(output_filename):
        os.remove(output_filename)

    # --- YOUTUBE BLOKUNU AŞMAQ ÜÇÜN AYARLAR ---
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_filename,
        'quiet': True,
        'no_warnings': True,
        # Bu hissə YouTube-u aldadır ki, guya biz Android telefonuq
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
            }
        },
        # IPv4 istifadəsini məcbur edirik (Server xətalarını azaldır)
        'source_address': '0.0.0.0', 
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=True)
            
            local_video_link = f"{TUNNEL_URL}/get_video"
            
            return {
                "status": "success",
                "title": info.get('title', 'Video'),
                "video_url": local_video_link,
                "thumbnail": info.get('thumbnail', '')
            }
    except Exception as e:
        print(f"Xəta: {e}")
        # Xəta mesajını qısa qaytarırıq ki, ekranda çox yer tutmasın
        return {"status": "error", "message": "YouTube Serveri Blokladı. Bir az sonra yoxlayın."}

@app.get("/get_video")
def get_video_file():
    file_path = "video.mp4"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4", filename="yuklenen_video.mp4")
    else:
        return {"error": "Fayl tapılmadı"}
