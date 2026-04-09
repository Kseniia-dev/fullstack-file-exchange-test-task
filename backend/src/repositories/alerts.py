from sqlalchemy import Select, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Alert


class AlertsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _base_query(self) -> Select[tuple[Alert]]:
        return select(Alert).order_by(Alert.created_at.desc(), Alert.id.desc())

    async def list_paginated(self, offset: int, limit: int) -> tuple[list[Alert], int]:
        total = await self.session.scalar(select(func.count()).select_from(Alert))
        result = await self.session.execute(self._base_query().offset(offset).limit(limit))
        return list(result.scalars().all()), int(total or 0)

    async def create(self, file_id: str, level: str, message: str) -> Alert:
        alert = Alert(file_id=file_id, level=level, message=message)
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert

    async def delete_for_file(self, file_id: str) -> None:
        await self.session.execute(delete(Alert).where(Alert.file_id == file_id))
