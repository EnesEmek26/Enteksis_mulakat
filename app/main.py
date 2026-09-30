import os
import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]
app = FastAPI()

def init_db():
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                service TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
        """)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    with psycopg.connect(DATABASE_URL) as conn:
        n = conn.execute("SELECT count(*) FROM requests").fetchone()[0]
    return {"status": "ok", "kayit_sayisi": n}