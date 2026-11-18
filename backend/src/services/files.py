import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, status
from starlette.datastructures import UploadFile

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.models import StoredFile
from src.repositories.alerts import AlertsRepository
from src.repositories.files import FilesRepository
from src.schemas import FilesPage, PageParams


settings = get_settings()


async def list_files(session: AsyncSession, params: PageParams) -> FilesPage:
    repository = FilesRepository(session)
    items, total = await repository.list_paginated(offset=params.offset, limit=params.per_page)
    return FilesPage.create(items=items, total=total, params=params)


async def get_file(session: AsyncSession, file_id: str) -> StoredFile:
    repository = FilesRepository(session)
    file_item = await repository.get(file_id)
    if not file_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return file_item


async def create_file(session: AsyncSession, title: str, upload_file: UploadFile) -> StoredFile:
    content = await upload_file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")

    file_id = str(uuid4())
    suffix = Path(upload_file.filename or "").suffix
    stored_name = f"{file_id}{suffix}"
    stored_path = settings.storage_dir / stored_name
    stored_path.write_bytes(content)

    file_item = StoredFile(
        id=file_id,
        title=title.strip(),
        original_name=upload_file.filename or stored_name,
        stored_name=stored_name,
        mime_type=upload_file.content_type or mimetypes.guess_type(stored_name)[0] or "application/octet-stream",
        size=len(content),
        processing_status="uploaded",
    )
    repository = FilesRepository(session)
    return await repository.create(file_item)


async def update_file(session: AsyncSession, file_id: str, title: str) -> StoredFile:
    repository = FilesRepository(session)
    file_item = await repository.get(file_id)
    if not file_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return await repository.update_title(file_item, title.strip())


async def delete_file(session: AsyncSession, file_id: str) -> None:
    repository = FilesRepository(session)
    file_item = await repository.get(file_id)
    if not file_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    stored_path = settings.storage_dir / file_item.stored_name
    if stored_path.exists():
        stored_path.unlink()

    alerts_repository = AlertsRepository(session)
    await alerts_repository.delete_for_file(file_id)
    await repository.delete(file_item)


async def get_file_path(session: AsyncSession, file_id: str) -> tuple[StoredFile, Path]:
    file_item = await get_file(session, file_id)
    stored_path = settings.storage_dir / file_item.stored_name
    if not stored_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")
    return file_item, stored_path
