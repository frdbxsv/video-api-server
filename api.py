from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp
import os

app = FastAPI()

# --- SƏNİN RENDER LİNKİN ---
TUNNEL_URL = "https://video-api-server-9b5n.onrender.com"

class VideoRequest(BaseModel):
    url: str

# 1. Videonu Serverə Yükləyən Hissə
@app.post("/download")
def download_video(request: VideoRequest):
    print(f"Video yüklənir: {request.url}")
    
    # Faylı 'video.mp4' adı ilə yadda saxlayacağıq
    output_filename = "video.mp4"
    
    # Əgər əvvəldən qalan video varsa, silirik ki, təzəsi yazılsın
    if os.path.exists(output_filename):
        os.remove(output_filename)

    # Bu, YouTube-un ən yaxşı işlədiyi sadə ayarlardır
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_filename, # Faylın adı
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Serverə yükləyirik (download=True)
            info = ydl.extract_info(request.url, download=True)
            
            # Telefona gedən link
            local_video_link = f"{TUNNEL_URL}/get_video"
            
            return {
                "status": "success",
                "title": info.get('title', 'Video'),
                "video_url": local_video_link, 
                "thumbnail": info.get('thumbnail', '')
            }
    except Exception as e:
        print(f"Xəta: {e}")
        return {"status": "error", "message": str(e)}

# 2. Videonu Telefona Verən Hissə
@app.get("/get_video")
def get_video_file():
    file_path = "video.mp4"
    # Əgər fayl varsa, telefona göndər
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4", filename="yuklenen_video.mp4")
    else:
        return {"error": "Fayl hələ yüklənməyib"}
