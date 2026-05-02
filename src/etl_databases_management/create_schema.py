from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv() 
db_url = os.getenv('database_url')

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url)

with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS gold"))
    conn.commit()