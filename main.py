from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pydantic import BaseModel
import os

pip install python-telegram-bot==20.6

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo
)
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8323701736:AAH7U-bVDOd-hgbbDtwQw7sHNv4Fn7gCI-4"
WEBAPP_URL = "https://gift-server-vyai.onrender.com"  # ссылка на Render

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎰 Открыть мини-игру", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать в Jackpot Mini App!", reply_markup=reply_markup)

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()


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

        from fastapi import Request
from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.post("/auth")
async def auth_user(request: Request):
    data = await request.json()
    tg_data = data.get("tg_data", {})
    user_id = tg_data.get("id")
    username = tg_data.get("username")

    # Проверяем, есть ли пользователь в базе
    user = supabase.table("users").select("*").eq("id", user_id).execute()
    if not user.data:
        supabase.table("users").insert({"id": user_id, "username": username, "balance": 0}).execute()

    return {"status": "ok", "user": tg_data}

    )
    db.commit()
    return {"message": "User created", "tg_id": user.tg_id}

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("index.html")

