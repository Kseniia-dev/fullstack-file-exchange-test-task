from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.schemas import PageParams


def get_page_params(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=100),
) -> PageParams:
    return PageParams(page=page, per_page=per_page)


SessionDep = Depends(get_session)
PageParamsDep = Depends(get_page_params)
