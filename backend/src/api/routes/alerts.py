from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_page_params
from src.db import get_session
from src.schemas import AlertsPage, PageParams
from src.services.alerts import list_alerts


router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertsPage)
async def list_alerts_view(
    params: PageParams = Depends(get_page_params),
    session: AsyncSession = Depends(get_session),
):
    return await list_alerts(session=session, params=params)
