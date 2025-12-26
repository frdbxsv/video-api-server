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
    
    # Köhnə faylı silirik
    if os.path.exists(output_filename):
        os.remove(output_filename)

    # STANDART AYARLAR (YouTube və TikTok üçün ən yaxşısı)
    ydl_opts = {
        'format': 'best', # Ən yaxşı keyfiyyət
        'outtmpl': output_filename,
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Videonu yükləyirik
            info = ydl.extract_info(request.url, download=True)
            
            # Telefona gedəcək link
            local_video_link = f"{TUNNEL_URL}/get_video"
            
            return {
                "status": "success",
                "title": info.get('title', 'Video'),
                "video_url": local_video_link,
                "thumbnail": info.get('thumbnail', '')
            }
    except Exception as e:
        # İndi əsl xətanı göstərəcək (Instagram xətası yazmayacaq)
        print(f"Xəta: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/get_video")
def get_video_file():
    file_path = "video.mp4"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4", filename="yuklenen_video.mp4")
    else:
        return {"error": "Fayl tapılmadı"}
