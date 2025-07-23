import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.logging import setup_logging
from api.routes import auth, history, detect_image, detect_video, detect_stream
from database import Base, engine

# create tables
Base.metadata.create_all(bind=engine)

setup_logging()
app = FastAPI(title="Deepfake Detection API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(detect_image.router, prefix="/api")
app.include_router(detect_video.router, prefix="/api")
app.include_router(detect_stream.router, prefix="/api")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
