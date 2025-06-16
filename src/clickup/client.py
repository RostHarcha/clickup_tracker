import asyncio
import logging
from datetime import datetime
from itertools import chain
from typing import TypeVar

from aiohttp import ClientSession
from aiohttp.typedefs import Query
from pydantic import BaseModel

from src.clickup.models import (
    Folder,
    FolderList,
    Space,
    SpaceList,
    TrackedTime,
    TrackedTimeList,
)

T = TypeVar('T', bound=BaseModel)


class ClickUpClient:
    def __init__(self, api_token: str) -> None:
        self._session = ClientSession(
            base_url='https://api.clickup.com',
            headers={
                'Authorization': api_token,
            },
        )
        self._logger = logging.getLogger(self.__class__.__name__)

    async def close(self) -> None:
        await self._session.close()

    async def _get(self, url, model: type[T], *, params: Query = None) -> T:
        async with self._session.get(url, params=params) as response:
            self._logger.info('"GET %s" %d', response.url, response.status)
            return model.model_validate_json(await response.read())

    async def get_spaces(self, team_id: int) -> list[Space]:
        return (
            await self._get(f'/api/v2/team/{team_id}/space', SpaceList)
        ).spaces

    async def get_folder_list(self, space_id: int) -> list[Folder]:
        return (
            await self._get(f'/api/v2/space/{space_id}/folder', FolderList)
        ).folders

    async def get_tracked_time_list(
        self,
        team_id: int,
        start_date: datetime,
        end_date: datetime,
        folder_id: int,
    ) -> list[TrackedTime]:
        return (
            await self._get(
                f'/api/v2/team/{team_id}/time_entries',
                TrackedTimeList,
                params={
                    'start_date': int(start_date.timestamp() * 1000),
                    'end_date': int(end_date.timestamp() * 1000),
                    'folder_id': folder_id,
                },
            )
        ).data

    async def get_folders(self, team_id: int) -> list[Folder]:
        spaces = await self.get_spaces(team_id)
        results = await asyncio.gather(
            *[self.get_folder_list(space.id) for space in spaces]
        )
        return list(chain(*results))

    async def get_tracked_times(
        self, team_id: int, start_date: datetime, end_date: datetime
    ):
        folders = await self.get_folders(team_id)
        results = await asyncio.gather(
            *[
                self.get_tracked_time_list(
                    team_id, start_date, end_date, folder.id
                )
                for folder in folders
            ]
        )
        return zip(folders, results, strict=True)
