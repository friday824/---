from arq.connections import RedisSettings

from backend.app.config import settings


class WorkerSettings:
    functions = ["backend.app.worker.jobs.run_video_pipeline"]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 1
    job_timeout = 600
    poll_delay = 0.5
