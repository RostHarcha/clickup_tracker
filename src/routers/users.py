from fastapi import APIRouter

from src.database import SessionDep, User, UserCreate, UserPublic, UserUpdate
from src.headers import ClickUpApiTokenHeaders

router = APIRouter(
    prefix='/users',
    tags=['users'],
)


@router.post('/', response_model=UserPublic)
async def create_user(user: UserCreate, session: SessionDep):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get('/me', response_model=UserPublic)
async def get_user(headers: ClickUpApiTokenHeaders, session: SessionDep):
    return headers.get_user(session)


@router.patch('/me', response_model=UserPublic)
async def update_user(
    headers: ClickUpApiTokenHeaders, user: UserUpdate, session: SessionDep
):
    db_user = headers.get_user(session)
    user_data = user.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
