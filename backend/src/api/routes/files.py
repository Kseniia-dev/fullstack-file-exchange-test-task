from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.datastructures import UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.api.dependencies import get_page_params
from src.db import get_session
from src.schemas import FileItem, FilesPage, FileUpdate, PageParams
from src.services.files import create_file, delete_file, get_file, get_file_path, list_files, update_file
from src.tasks import enqueue_file_processing


router = APIRouter(prefix="/files", tags=["files"])


@router.get("", response_model=FilesPage)
async def list_files_view(
    params: PageParams = Depends(get_page_params),
    session: AsyncSession = Depends(get_session),
):
    return await list_files(session=session, params=params)


@router.post("", response_model=FileItem, status_code=status.HTTP_201_CREATED)
async def create_file_view(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        form = await request.form()
    except AssertionError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Multipart support is not installed on the server",
        ) from error

    title = str(form.get("title", "")).strip()
    file = form.get("file")

    if not title:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Title is required")
    if not isinstance(file, UploadFile):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="File is required")

    file_item = await create_file(session=session, title=title, upload_file=file)
    enqueue_file_processing(file_item.id)
    return file_item


@router.get("/{file_id}", response_model=FileItem)
async def get_file_view(file_id: str, session: AsyncSession = Depends(get_session)):
    return await get_file(session=session, file_id=file_id)


@router.patch("/{file_id}", response_model=FileItem)
async def update_file_view(
    file_id: str,
    payload: FileUpdate,
    session: AsyncSession = Depends(get_session),
):
    return await update_file(session=session, file_id=file_id, title=payload.title)


@router.get("/{file_id}/download")
async def download_file(file_id: str, session: AsyncSession = Depends(get_session)):
    file_item, stored_path = await get_file_path(session=session, file_id=file_id)
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file_view(file_id: str, session: AsyncSession = Depends(get_session)):
    await delete_file(session=session, file_id=file_id)
