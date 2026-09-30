import logging
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

logger = logging.getLogger("app")

FIELD_MESSAGES = {
    "name": "İsim 2-80 karakter olmalı.",
    "email": "Geçerli bir e-posta adresi gir.",
    "service": "Listeden bir hizmet seç.",
    "message": "Açıklama 10-1000 karakter olmalı.",
}


def init_db():
    with psycopg.connect(DATABASE_URL, connect_timeout=5) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS requests (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                service TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


class RequestIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    service: Literal["gorev-toplama", "hatirlatma", "haftalik-rapor", "diger"]
    message: str = Field(min_length=10, max_length=1000)
    website: str = Field(default="", max_length=200)  # honeypot

    @field_validator("email")
    @classmethod
    def email_length(cls, v):
        if len(v) > 254:
            raise ValueError("too long")
        return v


@app.exception_handler(RequestValidationError)
async def validation_handler(request, exc):
    errors = {}
    for e in exc.errors():
        field = str(e["loc"][-1]) if e["loc"] else "body"
        errors.setdefault(field, FIELD_MESSAGES.get(field, "Geçersiz değer."))
    return JSONResponse(status_code=422, content={"errors": errors})


@app.get("/health")
def health():
    with psycopg.connect(DATABASE_URL, connect_timeout=5) as conn:
        n = conn.execute("SELECT count(*) FROM requests").fetchone()[0]
    return {"status": "ok", "kayit_sayisi": n}


@app.post("/api/requests", status_code=201)
def create_request(body: RequestIn):
    if body.website:
        return JSONResponse(status_code=400, content={"error": "Geçersiz istek."})
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=5) as conn:
            row = conn.execute(
                "INSERT INTO requests (name, email, service, message) "
                "VALUES (%s, %s, %s, %s) RETURNING id",
                (body.name, body.email, body.service, body.message),
            ).fetchone()
    except psycopg.Error:
        logger.exception("Kayıt yazılamadı")
        return JSONResponse(
            status_code=500,
            content={"error": "Talebin kaydedilemedi. Lütfen tekrar dene."},
        )
    return {"id": row[0]}


@app.get("/api/requests")
def list_requests(x_admin_token: str = Header(default="")):
    if not ADMIN_TOKEN or not secrets.compare_digest(
        x_admin_token.encode(), ADMIN_TOKEN.encode()
    ):
        raise HTTPException(status_code=401, detail="Yetkisiz")
    with psycopg.connect(DATABASE_URL, connect_timeout=5) as conn:
        rows = conn.execute(
            "SELECT id, name, email, service, message, created_at "
            "FROM requests ORDER BY id DESC LIMIT 50"
        ).fetchall()
    return [
        {"id": r[0], "name": r[1], "email": r[2], "service": r[3],
         "message": r[4], "created_at": r[5].isoformat()}
        for r in rows
    ]



app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")