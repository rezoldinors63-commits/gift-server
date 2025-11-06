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

from fastapi import FastAPI, Request
from supabase import create_client
import os

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.post("/deposit")
async def deposit(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    amount = float(data.get("amount", 0))

    if amount <= 0:
        return {"status": "error", "message": "Некорректная сумма"}

    # Проверяем есть ли пользователь
    user = supabase.table("users_balance").select("*").eq("user_id", user_id).execute()
    if user.data:
        # Обновляем баланс и выдаём тикеты (1 тикет за 10 TON, например)
        new_balance = float(user.data[0]["balance"]) + amount
        new_tickets = int(user.data[0]["tickets"]) + int(amount // 10)
        supabase.table("users_balance").update({
            "balance": new_balance,
            "tickets": new_tickets,
            "updated_at": "now()"
        }).eq("user_id", user_id).execute()
    else:
        # Если новый пользователь
        new_tickets = int(amount // 10)
        supabase.table("users_balance").insert({
            "user_id": user_id,
            "balance": amount,
            "tickets": new_tickets
        }).execute()

    return {"status": "ok", "balance": new_balance, "tickets": new_tickets}

class DepositRequest(BaseModel):
    user_id: int         # Telegram user id или внутренний id
    amount: float        # сумма в TON (или в вашей валюте)
    source: str = "manual"  # "cryptobot", "telegram_gift", "ton", "manual"
    external_id: str | None = None  # id транзакции от платёжной системы (invoice id)

DEPOSIT_SECRET = os.getenv("DEPOSIT_SECRET", "change_this_secret")  # в проде положи реальный секрет в env

@app.post("/deposit")
async def deposit(req: DepositRequest, x_deposit_secret: str | None = Header(None)):
    # Простая авторизация: webhook/криптобот должен поставить правильный X-DEPOSIT-SECRET
    if DEPOSIT_SECRET and x_deposit_secret != DEPOSIT_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = req.user_id
    amount = round(float(req.amount), 8)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    # Логика тикетов: допустим 1 тикет за каждые 10 TON
    TICKET_RATE = 1.0

    # Получим текущую запись пользователя
    res = supabase.table("users_balance").select("*").eq("user_id", user_id).limit(1).execute()
    existing = res.data[0] if res.data else None

    if existing:
        # Обновляем баланс и тикеты
        current_balance = float(existing.get("balance", 0))
        current_tickets = int(existing.get("tickets", 0))
        new_balance = round(current_balance + amount, 8)
        added_tickets = int((current_balance + amount) // TICKET_RATE) - int(current_balance // TICKET_RATE)
        # проще: выдаём тикеты по сумме пополнения
        added_tickets = int(amount // TICKET_RATE)
        new_tickets = current_tickets + added_tickets

        update = {"balance": new_balance, "tickets": new_tickets}
        supabase.table("users_balance").update(update).eq("user_id", user_id).execute()
    else:
        # Создаём запись
        new_balance = amount
        new_tickets = int(amount // TICKET_RATE)
        supabase.table("users_balance").insert({
            "user_id": user_id,
            "balance": new_balance,
            "tickets": new_tickets
        }).execute()

    return {"status": "ok", "user_id": user_id, "balance": new_balance, "tickets": new_tickets}
os.getenv("SUPABASE_URL")


