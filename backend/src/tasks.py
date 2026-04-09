import asyncio

try:
    from celery import Celery
except ModuleNotFoundError:  # pragma: no cover - local fallback for limited environments
    class _SyncTask:
        def __init__(self, func):
            self.func = func

        def delay(self, *args, **kwargs):
            return self.func(*args, **kwargs)

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)

    class Celery:  # type: ignore[override]
        def __init__(self, *args, **kwargs) -> None:
            pass

        def task(self, func):
            return _SyncTask(func)

from src.core.config import get_settings
from src.db import async_session_maker
from src.services.processing import extract_file_metadata, scan_file_for_threats, send_file_alert


settings = get_settings()
celery_app = Celery("file_tasks", broker=settings.redis_url, backend=settings.redis_url)
_worker_loop: asyncio.AbstractEventLoop | None = None


def run_in_worker_loop(coroutine):
    global _worker_loop
    if _worker_loop is None or _worker_loop.is_closed():
        _worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_worker_loop)
    return _worker_loop.run_until_complete(coroutine)


async def process_file(file_id: str) -> None:
    async with async_session_maker() as session:
        await scan_file_for_threats(session, file_id)
        await extract_file_metadata(session, file_id)
        await send_file_alert(session, file_id)


def enqueue_file_processing(file_id: str) -> None:
    process_uploaded_file.delay(file_id)


@celery_app.task
def process_uploaded_file(file_id: str) -> None:
    run_in_worker_loop(process_file(file_id))
