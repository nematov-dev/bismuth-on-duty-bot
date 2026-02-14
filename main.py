import json
import asyncio
import logging
import pytz 
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from decouple import config

# Logging
logging.basicConfig(level=logging.INFO)

# --- Sozlamalar ---
TOKEN = config("TOKEN")
ADMIN_ID = config("ADMIN_ID", cast=int)
GROUP_ID = config("GROUP_ID", cast=int)

# O'zbekiston vaqt mintaqasi
UZB_TZ = pytz.timezone('Asia/Tashkent')

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Schedulerni O'zbekiston vaqtiga sozlaymiz
scheduler = AsyncIOScheduler(timezone=UZB_TZ)

class UserForm(StatesGroup):
    name = State()
    birthday = State()
    is_duty_eligible = State()

# Ma'lumotlar bilan ishlash
def load_data():
    try:
        with open('data.json', 'r') as f:
            content = f.read()
            if not content:
                return {"users": [], "last_duty_index": 0}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"users": [], "last_duty_index": 0}

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

# Avtomatik vazifa
async def daily_job():
    data = load_data()
    # Hozirgi vaqtni O'zbekiston vaqti bilan olish
    now = datetime.now(UZB_TZ)
    today_str = now.strftime("%d-%m")
    tomorrow_str = (now + timedelta(days=1)).strftime("%d-%m")
    
    # Tug'ilgan kunlar
    for u in data['users']:
        if u['birthday'] == today_str:
            tabrik = (
                f"🎉 **Bugun guruhimizda bayram!**\n\n"
                f"🌟 Hurmatli **{u['name']}**, sizni bugungi tavallud ayyomingiz bilan chin qalbdan muborakbod etamiz!\n\n"
                f"Sizga dunyodagi eng ezgu tilaklarni — sog'lik-salomatlik, oilaviy baxt va ishlaringizda ulkan zafarlar tilaymiz. "
                f"Yuzingizdan kulgu, qalbingizdan quvonch hech qachon arimasin!\n\n"
                f"😊 Hurmat bilan, Bismuth Jamoasi!"
            )
            await bot.send_message(GROUP_ID, tabrik, parse_mode="Markdown")

        if u['birthday'] == tomorrow_str:
            await bot.send_message(GROUP_ID, f"⚠️ Diqqat Diqqat! Ertaga **{u['name']}**ning tug'ilgan kuni. Eslatib o'tamiz!", parse_mode="Markdown")

    # Navbatchilik (Avtomatik aylanish)
    duty_pool = [u for u in data['users'] if u.get('can_be_duty') == True]
    if duty_pool:
        idx = data.get('last_duty_index', 0)
        if idx >= len(duty_pool):
            idx = 0
            
        current_duty = duty_pool[idx]
        await bot.send_message(GROUP_ID, f"🔔 Bugun navbatchi: **{current_duty['name']}**", parse_mode="Markdown")
        
        data['last_duty_index'] = idx + 1
        save_data(data)

# --- Admin Panel ---
@dp.message(Command("start"), F.from_user.id == ADMIN_ID)
async def cmd_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="➕ Xodim qo'shish"), types.KeyboardButton(text="📋 Ro'yxat")],
        [types.KeyboardButton(text="🗑 O'chirish (Tozalash)")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(f"Boshqaruv paneli faollashdi. Server vaqti O'zbekistonga (UTC+5) sozlandi.", reply_markup=keyboard)

@dp.message(F.text == "➕ Xodim qo'shish", F.from_user.id == ADMIN_ID)
async def add_user_step1(message: types.Message, state: FSMContext):
    await state.set_state(UserForm.name)
    await message.answer("Xodimning Ism-Familiyasi:")

@dp.message(UserForm.name)
async def add_user_step2(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(UserForm.birthday)
    await message.answer("Tug'ilgan kuni (masalan: 14-02):")

@dp.message(UserForm.birthday)
async def add_user_step3(message: types.Message, state: FSMContext):
    await state.update_data(birthday=message.text)
    await state.set_state(UserForm.is_duty_eligible)
    kb = [
        [types.InlineKeyboardButton(text="Ha (Navbatchi)", callback_data="duty_yes")],
        [types.InlineKeyboardButton(text="Yo'q (Rahbar)", callback_data="duty_no")]
    ]
    await message.answer("Navbatchilikka qo'shilsinmi?", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("duty_"))
async def finalize_user(callback: types.CallbackQuery, state: FSMContext):
    can_duty = (callback.data == "duty_yes")
    user_data = await state.get_data()
    data = load_data()
    data['users'].append({
        "name": user_data['name'],
        "birthday": user_data['birthday'],
        "can_be_duty": can_duty
    })
    save_data(data)
    await state.clear()
    await callback.message.edit_text(f"✅ {user_data['name']} bazaga qo'shildi.")

@dp.message(F.text == "📋 Ro'yxat", F.from_user.id == ADMIN_ID)
async def list_users(message: types.Message):
    data = load_data()
    if not data['users']:
        await message.answer("Ro'yxat bo'sh.")
        return
    text = "📂 **Xodimlar:**\n\n"
    for idx, u in enumerate(data['users']):
        icon = "🧑‍✈️" if u.get('can_be_duty') else "👔"
        text += f"{idx+1}. {icon} {u['name']} - {u['birthday']}\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "🗑 O'chirish (Tozalash)", F.from_user.id == ADMIN_ID)
async def clear_data(message: types.Message):
    save_data({"users": [], "last_duty_index": 0})
    await message.answer("Baza tozalandi.")

# Start
async def main():
    # Germaniya serverida bo'lsa ham aynan Toshkent vaqti bilan 10:00 da ishlaydi
    scheduler.add_job(daily_job, 'cron', hour=10, minute=0)
    scheduler.start()
    
    logging.info("Bot ishga tushdi (Tashkent TimeZone).")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass