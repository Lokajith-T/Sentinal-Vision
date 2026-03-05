from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import asyncio
import database
import models
import video_engine
import uvicorn
import time
from contextlib import asynccontextmanager

# Define your cameras here! You can add as many as you want.
# Format: "Camera Name": "source"
CAMERA_SOURCES = {
    "cam1": 0,                                     # Your Laptop Webcam
    "cam2": "http://192.168.0.101:8080/video"        # Your Phone IP Webcam 
}

# Global registry of active camera engines
engines = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global engines
    
    # Initialize a video engine for each camera in the dictionary
    for cam_id, source in CAMERA_SOURCES.items():
        engine = video_engine.VideoEngine(source=source)
        engine.start()
        engines[cam_id] = engine
    
    yield
    
    # Clean up all cameras gracefully
    for engine in engines.values():
        if engine:
            engine.stop()
    time.sleep(0.5)

app = FastAPI(title="Sentinel Vision API", lifespan=lifespan)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
models.Base.metadata.create_all(bind=database.engine)

def gen_frames(camera_id: str):
    engine = engines.get(camera_id)
    if not engine:
        return

    while True:
        frame_bytes = engine.get_frame_bytes()
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.1)

@app.get("/video-feed/{camera_id}")
def video_feed(camera_id: str):
    if camera_id not in engines:
        return Response(status_code=404, content="Camera not found")
    return StreamingResponse(gen_frames(camera_id), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/alerts")
def get_live_alerts():
    # Aggregate alerts from all cameras, sort by time, and get the latest 20
    all_alerts = []
    for eng in engines.values():
        all_alerts.extend(eng.latest_alerts)
    
    # Sort descending by timestamp
    all_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
    return {"alerts": all_alerts[:20]}

@app.get("/events")
def get_events(limit: int = 50, db: Session = Depends(database.get_db)):
    events = db.query(models.EventDB).order_by(models.EventDB.timestamp.desc()).limit(limit).all()
    return {"events": events}

@app.get("/heatmap/{camera_id}")
def get_heatmap(camera_id: str):
    engine = engines.get(camera_id)
    if not engine:
        return Response(status_code=404, content="Camera not found")
        
    heatmap_bytes = engine.generate_heatmap()
    return Response(content=heatmap_bytes, media_type="image/jpeg")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
