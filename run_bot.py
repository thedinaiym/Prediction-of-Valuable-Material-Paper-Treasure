import asyncio
import json
import logging
from typing import List, Dict
import aiofiles  # Добавляем библиотеку для асинхронной работы с файлами

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from tabulate import tabulate
import os
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация бота
class Config:
    BOT_TOKEN = '7792128129:AAE5dIQdUavz4aDPGBCOiyJ9A6sL_FjqkNY'

async def load_json_data(file_path: str) -> List[Dict]:
    """
    Асинхронная загрузка данных из JSON файла с использованием aiofiles
    """
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
    """
    Получение первых 7 строк, исключая строку с заголовками
    """
    # Удаляем первую строку с заголовками
    filtered_data = [item for item in data if item['Дата'] != 'Дата']
    
    # Возвращаем первые 7 строк
    return filtered_data[:6]

def format_gold_data(data: List[Dict]) -> str:
    """
    Форматирование данных о золоте в красивую таблицу
    """
    if not data:
        return "Нет данных для отображения"
    
    # Исключаем первую строку (заголовки) из форматирования
    headers = list(data[0].keys())
    table_data = [list(item.values()) for item in data]
    
    # Создание таблицы с помощью tabulate
    table = tabulate(
        table_data, 
        headers=headers, 
        tablefmt='pipe', 
        numalign='right', 
        stralign='left'
    )
    
    return f"```\n{table}\n```"

async def cmd_gold(message: Message):
    """
    Обработчик команды /gold
    """
    json_file_path = 'gold_data.json'
    
    # Загрузка данных
    all_data = await load_json_data(json_file_path)
    
    if not all_data:
        await message.answer("Не удалось загрузить данные о золоте.")
        return
    
    # Получение данных с последней датой
    latest_date_data = get_latest_date_data(all_data)
    
    if not latest_date_data:
        await message.answer("Нет данных для отображения.")
        return
    
    # Форматирование данных
    formatted_data = format_gold_data(latest_date_data)
    
    # Экранирование специальных символов для MarkdownV2
    def escape_markdown_v2(text):
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return ''.join('\\' + char if char in escape_chars else char for char in text)
    
    escaped_date = escape_markdown_v2(latest_date_data[0]['Дата'])
    
    # Отправка сообщения
    await message.answer(
        f"📊 Данные о золотых слитках на {escaped_date}:\n\n{formatted_data}", 
        parse_mode='MarkdownV2'
    )

async def cmd_start(message: Message):
    """
    Обработчик команды /start
    """
    await message.answer(
        "Привет! Используйте /gold для получения данных о золотых слитках.\n"
        "Данные будут показаны за последнюю доступную дату."
    )

async def main():
    """
    Основная асинхронная функция запуска бота
    """
    # Инициализация бота и диспетчера
    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация хэндлеров
    dp.message.register(cmd_start, Command(commands=['start']))
    dp.message.register(cmd_gold, Command(commands=['gold']))

    # Информирование о старте
    logger.info('Бот запущен')

    try:
        # Старт поллинга
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