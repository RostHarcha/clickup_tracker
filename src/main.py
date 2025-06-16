import logging

from fastapi import FastAPI

from src.database import create_db_and_tables
from src.routers import reports, users

logging.basicConfig(level=logging.INFO)


app = FastAPI(on_startup=[create_db_and_tables])
app.include_router(users.router)
app.include_router(reports.router)
