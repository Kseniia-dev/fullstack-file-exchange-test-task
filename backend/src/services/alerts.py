from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.alerts import AlertsRepository
from src.schemas import AlertsPage, PageParams


async def list_alerts(session: AsyncSession, params: PageParams) -> AlertsPage:
    repository = AlertsRepository(session)
    items, total = await repository.list_paginated(offset=params.offset, limit=params.per_page)
    return AlertsPage.create(items=items, total=total, params=params)


async def create_alert(session: AsyncSession, file_id: str, level: str, message: str):
    repository = AlertsRepository(session)
    return await repository.create(file_id=file_id, level=level, message=message)
