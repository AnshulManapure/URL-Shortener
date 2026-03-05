from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os

load_dotenv()

postgres_user = os.getenv("POSTGRES_USER")
postgres_pass = os.getenv("POSTGRES_PASSWORD")

db_url = f"postgresql://{postgres_user}:{postgres_pass}@localhost:5432/URL-Shortener"
engine = create_engine(db_url)
session = sessionmaker(bind=engine, autoflush=False, autocommit=False)