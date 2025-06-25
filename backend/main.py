import uvicorn
from fastapi import FastAPI
from utils.logging import setup_logging
from api.routes import auth, history, detect_image, detect_video, detect_stream
from database import Base, engine

# create tables
Base.metadata.create_all(bind=engine)

setup_logging()
app = FastAPI(title="Deepfake Detection API")

app.include_router(auth.router)
app.include_router(history.router)
app.include_router(detect_image.router)
app.include_router(detect_video.router)
app.include_router(detect_stream.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
