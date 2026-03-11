from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os

load_dotenv()

# POSTGRES_USER = os.getenv("POSTGRES_USER")
# POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD")
POSTGRES_URL = os.getenv("POSTGRES_URL")

db_url = POSTGRES_URL
engine = create_engine(db_url)
session = sessionmaker(bind=engine, autoflush=False, autocommit=False)