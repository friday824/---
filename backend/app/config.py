from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # DashScope
    dashscope_api_key: str = ""

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/app.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str = "change-me-to-a-random-secret-string-at-least-32-chars"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Storage paths
    data_dir: Path = Path("data")
    video_output_dir: Path = Path("data/videos")
    image_output_dir: Path = Path("data/images")
    audio_output_dir: Path = Path("data/audio")
    bgm_library_dir: Path = Path("data/bgm")

    # Limits
    max_videos_per_user_day: int = 5
    max_scenes: int = 8
    max_video_duration_s: int = 90

    # CORS
    cors_origins: list[str] = ["http://localhost:5173"]

    # Storage backend: "local" or "oss"
    storage_backend: str = "local"

    # OSS (only when storage_backend=oss)
    oss_access_key_id: str = ""
    oss_access_key_secret: str = ""
    oss_endpoint: str = "oss-cn-hangzhou.aliyuncs.com"
    oss_bucket_name: str = "diary2anime-videos"


settings = Settings()
