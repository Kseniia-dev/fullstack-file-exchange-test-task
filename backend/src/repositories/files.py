from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import StoredFile


class FilesRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _base_query(self) -> Select[tuple[StoredFile]]:
        return select(StoredFile).order_by(StoredFile.created_at.desc(), StoredFile.id.desc())

    async def list_paginated(self, offset: int, limit: int) -> tuple[list[StoredFile], int]:
        total = await self.session.scalar(select(func.count()).select_from(StoredFile))
        result = await self.session.execute(self._base_query().offset(offset).limit(limit))
        return list(result.scalars().all()), int(total or 0)

    async def get(self, file_id: str) -> StoredFile | None:
        return await self.session.get(StoredFile, file_id)

    async def create(self, file_item: StoredFile) -> StoredFile:
        self.session.add(file_item)
        await self.session.commit()
        await self.session.refresh(file_item)
        return file_item

    async def update_title(self, file_item: StoredFile, title: str) -> StoredFile:
        file_item.title = title
        await self.session.commit()
        await self.session.refresh(file_item)
        return file_item

    async def delete(self, file_item: StoredFile) -> None:
        await self.session.delete(file_item)
        await self.session.commit()
