from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    MAX_FILE_SIZE: int = 50 * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS: tuple = (".jpg", ".jpeg", ".png")
    ALLOWED_VIDEO_EXTENSIONS: tuple = (".mp4", ".mov", ".avi")

    VIT_MODEL_PATH: str = "pretrained_models/vit_deepfake.pt"
    TIMESFORMER_MODEL_PATH: str = "pretrained_models/timesformer_deepfake.pt"
    SYNCNET_MODEL_PATH: str = "pretrained_models/syncnet.pth"

    TARGET_IMAGE_SIZE: int = 224
    CLIP_LENGTH: int = 16  # number of frames per video clip

    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    return Settings()
