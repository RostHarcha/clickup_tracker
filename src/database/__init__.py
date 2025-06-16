from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel

from src.database.session import engine, get_session
from src.database.user import User, UserCreate, UserPublic, UserUpdate

__all__ = [
    'SessionDep',
    'User',
    'UserCreate',
    'UserPublic',
    'UserUpdate',
    'create_db_and_tables',
]


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


SessionDep = Annotated[Session, Depends(get_session)]
