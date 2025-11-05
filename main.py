from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pydantic import BaseModel
import os

load_dotenv()

app = FastAPI()

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

@app.get("/")
def home():
    return {"status": "ok"}

class UserCreate(BaseModel):
    tg_id: str
    username: str | None = None

@app.post("/user/create")
def create_user(user: UserCreate):
    db = SessionLocal()
    db.execute(
        "INSERT INTO users (tg_id, username) VALUES (%s, %s) ON CONFLICT (tg_id) DO NOTHING",
        (user.tg_id, user.username or "anonymous")
    )
    db.commit()
    return {"message": "User created", "tg_id": user.tg_id}
