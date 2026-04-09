import asyncio
from io import BytesIO
from pathlib import Path
import shutil
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import UploadFile

from src.schemas import PageParams, PaginatedResponse
from src.services import files as files_service
from src.services import processing as processing_service


TEST_TMP_ROOT = Path(__file__).resolve().parent / ".tmp"


@pytest.fixture
def workspace_tmp_dir() -> Path:
    target = TEST_TMP_ROOT / "case"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    yield target
    if target.exists():
        shutil.rmtree(target)


def test_paginated_response_calculates_total_pages() -> None:
    params = PageParams(page=2, per_page=5)

    page = PaginatedResponse[int].create(items=[1, 2], total=12, params=params)

    assert page.page == 2
    assert page.per_page == 5
    assert page.total == 12
    assert page.total_pages == 3


def test_create_file_rejects_empty_upload(workspace_tmp_dir: Path) -> None:
    settings = SimpleNamespace(storage_dir=workspace_tmp_dir)
    original_settings = files_service.settings
    files_service.settings = settings

    session = AsyncMock()
    upload = UploadFile(filename="empty.txt", file=BytesIO(b""), headers={"content-type": "text/plain"})

    with pytest.raises(Exception) as error:
        asyncio.run(files_service.create_file(session=session, title="Empty", upload_file=upload))

    files_service.settings = original_settings
    assert "File is empty" in str(error.value)


def test_scan_marks_executable_file_as_suspicious() -> None:
    file_item = SimpleNamespace(
        original_name="payload.exe",
        size=128,
        mime_type="application/octet-stream",
        processing_status="uploaded",
        scan_status=None,
        scan_details=None,
        requires_attention=False,
    )
    session = AsyncMock()
    session.get = AsyncMock(return_value=file_item)

    asyncio.run(processing_service.scan_file_for_threats(session, "file-1"))

    assert file_item.processing_status == "processing"
    assert file_item.scan_status == "suspicious"
    assert "suspicious extension .exe" in file_item.scan_details
    assert file_item.requires_attention is True
    session.commit.assert_awaited_once()


def test_extract_text_metadata_uses_storage_file(workspace_tmp_dir: Path) -> None:
    stored_file = workspace_tmp_dir / "note.txt"
    stored_file.write_text("line-1\nline-2", encoding="utf-8")

    file_item = SimpleNamespace(
        stored_name="note.txt",
        original_name="note.txt",
        size=13,
        mime_type="text/plain",
        processing_status="processing",
        scan_status="clean",
        scan_details="no threats found",
        metadata_json=None,
    )
    session = AsyncMock()
    session.get = AsyncMock(return_value=file_item)

    original_settings = processing_service.settings
    processing_service.settings = SimpleNamespace(storage_dir=workspace_tmp_dir)

    asyncio.run(processing_service.extract_file_metadata(session, "file-1"))

    processing_service.settings = original_settings
    assert file_item.processing_status == "processed"
    assert file_item.metadata_json == {
        "extension": ".txt",
        "size_bytes": 13,
        "mime_type": "text/plain",
        "line_count": 2,
        "char_count": 13,
    }
    session.commit.assert_awaited_once()


def test_delete_file_removes_storage_and_related_alerts(
    workspace_tmp_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stored_file = workspace_tmp_dir / "file.txt"
    stored_file.write_text("payload", encoding="utf-8")
    file_item = SimpleNamespace(stored_name="file.txt")

    files_repository = SimpleNamespace(
        get=AsyncMock(return_value=file_item),
        delete=AsyncMock(),
    )
    alerts_repository = SimpleNamespace(delete_for_file=AsyncMock())

    monkeypatch.setattr(files_service, "FilesRepository", lambda session: files_repository)
    monkeypatch.setattr(files_service, "AlertsRepository", lambda session: alerts_repository)

    original_settings = files_service.settings
    files_service.settings = SimpleNamespace(storage_dir=workspace_tmp_dir)

    asyncio.run(files_service.delete_file(session=AsyncMock(), file_id="file-1"))

    files_service.settings = original_settings
    alerts_repository.delete_for_file.assert_awaited_once_with("file-1")
    files_repository.delete.assert_awaited_once_with(file_item)
    assert not stored_file.exists()
