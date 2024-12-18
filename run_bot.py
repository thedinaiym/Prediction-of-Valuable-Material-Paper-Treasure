import asyncio
import json
import logging
from typing import List, Dict
import aiofiles
import csv  # Добавлен для обработки CSV
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from tabulate import tabulate
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Config:
    BOT_TOKEN = '7792128129:AAE5dIQdUavz4aDPGBCOiyJ9A6sL_FjqkNY'


async def load_json_data(file_path: str) -> List[Dict]:
    try:
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
            content = await file.read()
            return json.loads(content)
    except FileNotFoundError:
        logger.error(f"Файл {file_path} не найден")
        return []
    except json.JSONDecodeError:
        logger.error(f"Ошибка декодирования JSON в файле {file_path}")
        return []


def get_latest_date_data(data: List[Dict]) -> List[Dict]:
    filtered_data = [item for item in data if item['Дата'] != 'Дата']
    return filtered_data[:6]


def format_table_data(data: List[Dict]) -> str:
    if not data:
        return "Нет данных для отображения"
    
    headers = list(data[0].keys())
    table_data = [list(item.values()) for item in data]
    
    table = tabulate(
        table_data, 
        headers=headers, 
        tablefmt='pipe', 
        numalign='right', 
        stralign='left'
    )
    
    return f"```\n{table}\n```"


async def cmd_kyrgyz_gold(message: Message):
    json_file_path = 'data/kyrgyz_gold.json'
    
    all_data = await load_json_data(json_file_path)
    
    if not all_data:
        await message.answer("Не удалось загрузить данные о золоте.")
        return
    
    latest_date_data = get_latest_date_data(all_data)
    
    if not latest_date_data:
        await message.answer("Нет данных для отображения.")
        return
    
    formatted_data = format_table_data(latest_date_data)
    
    def escape_markdown_v2(text):
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return ''.join('\\' + char if char in escape_chars else char for char in text)
    
    escaped_date = escape_markdown_v2(latest_date_data[0]['Дата'])
    
    await message.answer(
        f"📊 Данные о золотых слитках на {escaped_date}:\n\n{formatted_data}", 
        parse_mode='MarkdownV2'
    )


async def cmd_nbkr_gold(message: Message):
    json_file_path = 'data/nbkr.json'
    
    all_data = await load_json_data(json_file_path)
    
    if not all_data:
        await message.answer("Не удалось загрузить данные о золоте.")
        return
    
    latest_date_data = get_latest_date_data(all_data)
    
    if not latest_date_data:
        await message.answer("Нет данных для отображения.")
        return
    
    formatted_data = format_table_data(latest_date_data)
    
    def escape_markdown_v2(text):
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return ''.join('\\' + char if char in escape_chars else char for char in text)
    
    escaped_date = escape_markdown_v2(latest_date_data[0]['Дата'])
    
    await message.answer(
        f"📊 Данные о золотых слитках на {escaped_date}:\n\n{formatted_data}", 
        parse_mode='MarkdownV2'
    )


async def cmd_valuta(message: Message):
    csv_file_path = 'data/optima.csv'
    
    try:
        async with aiofiles.open(csv_file_path, mode='r', encoding='utf-8') as f:
            content = await f.read()
    except FileNotFoundError:
        await message.answer("Файл optima.csv не найден.")
        return
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {csv_file_path}: {e}")
        await message.answer("Произошла ошибка при загрузке данных.")
        return
    
    # Парсинг CSV
    reader = csv.DictReader(content.splitlines())
    data = [row for row in reader]
    
    # Извлечение первых 4 строк
    first_four = data[:4]  # Исправлено с data[4:] на data[:4]
    
    if not first_four:
        await message.answer("Нет данных для отображения.")
        return
    
    formatted_data = format_table_data(first_four)
    
    # Получение даты из первой строки
    date = first_four[0].get('Дата', 'Неизвестно')
    
    def escape_markdown_v2(text):
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return ''.join('\\' + char if char in escape_chars else char for char in text)
    
    escaped_date = escape_markdown_v2(date)
    
    await message.answer(
        f"💱 Валютные курсы Оптима на {escaped_date}:\n\n{formatted_data}", 
        parse_mode='MarkdownV2'
    )


async def cmd_predict(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Перейти к прогнозу",
                    url="https://prediction-of-valuable-material-paper-treasure-aerdst8oymg9vg3.streamlit.app/"
                )
            ]
        ]
    )
    await message.answer(
        "Перейдите по кнопке ниже, чтобы сделать прогноз:",
        reply_markup=keyboard
    )


async def cmd_start(message: Message):
    await message.answer(
         "👋 **Добро пожаловать!**\n\n"
        "Я бот, который предоставляет актуальные данные о золотых слитках и валютных курсах.\n\n"
        "📊 **Доступные команды:**\n"
        "• `/kyrgyz_gold` — Данные о золотых слитках из Кыргызстана\n"
        "• `/nbkr_gold` — Данные от Национального банка Кыргызстана\n"
        "• `/valuta` — Валютные курсы Оптима\n"
        "• `/predict` — Получить прогнозы по ценам на золото\n\n"
        "🔍 **Как это работает:**\n"
        "Данные обновляются ежедневно и отображают информацию за последнюю доступную дату.\n\n"
        "ℹ️ **Дополнительная информация:**\n"
        "Используйте команды выше, чтобы получать свежие данные и прогнозы.\n"
        "Если у вас есть вопросы или предложения, свяжитесь с [разработчиком](https://t.me/thedinaiym)."
    )


async def main():
    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(cmd_start, Command(commands=['start']))
    dp.message.register(cmd_kyrgyz_gold, Command(commands=['kyrgyz_gold']))
    dp.message.register(cmd_nbkr_gold, Command(commands=['nbkr_gold']))
    dp.message.register(cmd_valuta, Command(commands=['valuta']))  # Регистрация /valuta
    dp.message.register(cmd_predict, Command(commands=['predict']))

    logger.info('Бот запущен')

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f'Ошибка при работе бота: {e}')
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Бот остановлен')
