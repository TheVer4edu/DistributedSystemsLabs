import os
from os import getenv
from os.path import exists
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DOTENV_PATH = "../.env"

if exists(DOTENV_PATH):
    load_dotenv(DOTENV_PATH)

USER = getenv("POSTGRES_USER") or os.environ.get("POSTGRES_USER")
PASSWORD = getenv("POSTGRES_PASSWORD") or os.environ.get("POSTGRES_PASSWORD")
DB_NAME = getenv("POSTGRES_DB") or os.environ.get("POSTGRES_DB")
HOST = getenv("DB_URL") or "localhost"
DB_PORT = "5432"

db_url = f"postgresql://{USER}:{PASSWORD}@{HOST}:{DB_PORT}/{DB_NAME}"

print(db_url)


engine = create_engine(db_url, pool_size=20, max_overflow=0)
session = sessionmaker(engine)
