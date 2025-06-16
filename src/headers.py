from typing import Annotated

from fastapi import Header, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from src.database import User


class ClickUpApiTokenModel(BaseModel):
    clickup_api_token: str

    def get_user(self, session: Session) -> User:
        user = session.exec(
            select(User).where(User.clickup_api_token == self.clickup_api_token)
        ).first()
        if not user:
            raise HTTPException(status_code=404, detail='User not found')
        return user


ClickUpApiTokenHeaders = Annotated[ClickUpApiTokenModel, Header()]
