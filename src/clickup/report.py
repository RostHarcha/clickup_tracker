from collections import OrderedDict, defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from functools import cached_property

from prettytable import PrettyTable
from pydantic import BaseModel

from src.clickup.client import ClickUpClient
from src.clickup.utils import stringify_timedelta


class ReportRow(BaseModel):
    date: date
    project: str
    duration: timedelta


class Report(BaseModel):
    from_date: date
    to_date: date
    hourly_rate: Decimal
    data: tuple[ReportRow, ...]

    @cached_property
    def work_time(self) -> timedelta:
        return sum((row.duration for row in self.data), timedelta())

    @cached_property
    def total_hours(self) -> Decimal:
        return Decimal(self.work_time.total_seconds()) / 3600

    @cached_property
    def payment(self) -> int:
        return int(self.total_hours * self.hourly_rate)

    @cached_property
    def rows(self) -> tuple[ReportRow, ...]:
        return tuple(sorted(self.data, key=lambda x: x.date))

    @cached_property
    def project_time(self) -> OrderedDict[str, timedelta]:
        by_project = {}
        for row in self.data:
            by_project.setdefault(row.project, timedelta())
            by_project[row.project] += row.duration
        return OrderedDict(sorted(by_project.items()))

    @cached_property
    def date_time(self) -> OrderedDict[date, timedelta]:
        by_date = {}
        for row in self.data:
            by_date.setdefault(row.date, timedelta())
            by_date[row.date] += row.duration
        _date = self.from_date
        while _date <= self.to_date:
            by_date.setdefault(_date, timedelta(0))
            _date += timedelta(days=1)
        return OrderedDict(sorted(by_date.items()))

    @cached_property
    def projects_table(self):
        table = PrettyTable(('Проект', 'Отработка'), align='l')
        table.add_rows(
            [
                [proj, stringify_timedelta(td)]
                for proj, td in self.project_time.items()
            ]
        )
        return table

    @cached_property
    def daily_table(self):
        table = PrettyTable(('Дата', 'Отработка'), align='l')
        table.add_rows(
            [
                [date_, stringify_timedelta(td)]
                for date_, td in self.date_time.items()
            ]
        )
        return table

    @cached_property
    def summary_table(self):
        table = PrettyTable(
            ('Ставка, руб/ч', 'Отработано, ч', 'Выплата, руб'),
            min_table_width=70,
        )
        table.add_row(
            [
                str(self.hourly_rate),
                f'{self.total_hours:.2f}',
                str(self.payment),
            ]
        )
        return table

    def __str__(self) -> str:
        hours_table = PrettyTable(header=False, border=False)
        hours_table.add_row([str(self.projects_table), str(self.daily_table)])
        table = PrettyTable(
            title=f'{self.from_date:%d.%m.%y} - {self.to_date:%d.%m.%y}',
            header=False,
        )
        table.add_row([str(hours_table)])
        table.add_row([str(self.summary_table)])
        return str(table)

    @classmethod
    async def _get_folders_data(
        cls,
        api: ClickUpClient,
        team_id: int,
        from_dt: datetime,
        to_dt: datetime,
    ) -> tuple[ReportRow, ...]:
        data: list[ReportRow] = []
        for folder, tracked_time_list in await api.get_tracked_times(
            team_id, from_dt, to_dt
        ):
            by_dates = defaultdict(list)
            for tracked_time in tracked_time_list:
                by_dates[tracked_time.start_date].append(tracked_time)
            for date_, tracked_list in by_dates.items():
                data.append(
                    ReportRow(
                        date=date_,
                        project=folder.name,
                        duration=sum(
                            (
                                tracked_time.normalized_duration
                                for tracked_time in tracked_list
                            ),
                            timedelta(),
                        ),
                    )
                )
        return tuple(data)

    @classmethod
    async def _get_personal_folder_data(
        cls,
        api: ClickUpClient,
        team_id: int,
        from_dt: datetime,
        to_dt: datetime,
        folder_id: int,
    ) -> tuple[ReportRow, ...]:
        return tuple(
            ReportRow(
                date=tracked_time.start_date,
                project=f'(вне проектов) - {tracked_time.task.name}',
                duration=tracked_time.normalized_duration,
            )
            for tracked_time in await api.get_tracked_time_list(
                team_id, from_dt, to_dt, folder_id
            )
        )

    @classmethod
    async def create(
        cls,
        api_token: str,
        team_id: int,
        from_dt: datetime,
        to_dt: datetime,
        hourly_rate: Decimal,
        personal_folder_id: int | None,
    ):
        api = ClickUpClient(api_token)
        report = cls(
            from_date=from_dt.date(),
            to_date=to_dt.date(),
            hourly_rate=hourly_rate,
            data=(
                *await cls._get_folders_data(api, team_id, from_dt, to_dt),
                *(
                    await cls._get_personal_folder_data(
                        api, team_id, from_dt, to_dt, personal_folder_id
                    )
                    if personal_folder_id
                    else ()
                ),
            ),
        )
        await api.close()
        return report
