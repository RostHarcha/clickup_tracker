from datetime import date, datetime, time

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from src.clickup import Report
from src.database import SessionDep
from src.headers import ClickUpApiTokenHeaders
from src.settings import settings

router = APIRouter(
    prefix='/reports',
    tags=['reports'],
)


@router.get('/', response_class=PlainTextResponse)
async def get_report(
    headers: ClickUpApiTokenHeaders,
    from_date: date,
    to_date: date,
    session: SessionDep,
):
    user = headers.get_user(session)
    report = await Report.create(
        api_token=user.clickup_api_token,
        team_id=user.team_id,
        from_dt=datetime.combine(from_date, time.min, settings.time_zone),
        to_dt=datetime.combine(to_date, time.max, settings.time_zone),
        hourly_rate=user.hourly_rate,
        personal_folder_id=user.personal_folder_id,
    )
    return str(report)
