from datetime import date, datetime, timedelta
from functools import cached_property

from pydantic import BaseModel


class Space(BaseModel):
    id: int
    name: str


class SpaceList(BaseModel):
    spaces: list[Space]


class Folder(BaseModel):
    id: int
    name: str


class FolderList(BaseModel):
    folders: list[Folder]


class Task(BaseModel):
    id: str
    name: str


class User(BaseModel):
    id: int
    username: str
    email: str


class TrackedTime(BaseModel):
    id: int
    task: Task
    user: User
    duration: int
    start: int
    end: int

    @cached_property
    def start_date(self) -> date:
        return datetime.fromtimestamp(self.start / 1000).date()  # noqa: DTZ006

    @cached_property
    def normalized_duration(self) -> timedelta:
        return timedelta(milliseconds=self.duration)


class TrackedTimeList(BaseModel):
    data: list[TrackedTime]
