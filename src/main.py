def parse_args():
    from argparse import ArgumentParser

    from src.utils import parse_date

    parser = ArgumentParser()
    parser.add_argument(
        '--from_date',
        '--from',
        '-f',
        help='Start date. Format: DD[.MM[.YY]]',
    )
    parser.add_argument(
        '--to_date',
        '--to',
        '-t',
        help='Finish date. Format: DD[.MM[.YY]]',
    )
    args = parser.parse_args()
    args.from_date = parse_date(args.from_date, min=True)
    args.to_date = parse_date(args.to_date, max=True)
    return args


async def main():
    from src.report import Report
    from src.settings import settings

    args = parse_args()
    report = await Report.create(
        api_token=settings.api_token,
        team_id=settings.team_id,
        from_dt=args.from_date,
        to_dt=args.to_date,
        hourly_rate=settings.hourly_rate,
        personal_folder_id=settings.personal_folder_id,
    )
    print(report)  # noqa: T201


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
