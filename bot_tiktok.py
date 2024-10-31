import asyncio
import logging
import sys
import requests
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Filter, Command
from aiogram.types import Message, InputFile, URLInputFile, FSInputFile
from aiogram.utils.markdown import hbold
import bot_tiktok_database as database
from aiogram.client.bot import DefaultBotProperties
2
TOKEN = "7391245181:AAFgLQEqrb4iVukDyjyJ1kpFHZRXIxv8YkU"

dp = Dispatcher()

database.create_table_users()
database.create_table_convertations()

class LinkFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.text.startswith("http")

@dp.message(LinkFilter())
async def link_handler(message: Message) -> None:
    link = message.text

    msg = await message.answer("Пожалуйста, подождите, запрос обрабатывается")
    url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"

    querystring = {"url":link, "hd": "1"}

    headers = {
        "X-RapidAPI-Key": "1ea0bfd27dmsh3deb9178d0ea377p1bf47ajsnb78f8cd16d0f",
        "X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    try:
        video_link = response.json()['data']['play']
    except KeyError:
        await msg.edit_text('Ссылка оказалась неверной. Повторите попытку')
        database.add_convertation(message.from_user.id, status='Failed')
        return

    await msg.edit_text("Отправляю видео.\nСекундочку...")
    await msg.delete()
    await message.answer_video(URLInputFile(video_link))
    database.add_convertation(message.from_user.id, status='Done')

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет, {hbold(message.from_user.full_name)}!\nЭто загрузчик видео из тиктока без водяного знака.\nПросто отправь мне ссылку на видео.")
    database.add_user(message.from_user.id, message.from_user.username)

@dp.message(Command('28092000'))
async def command_start_handler(message: Message) -> None:
    users = database.get_users()
    convertations = database.get_convertations()
    with open('info.txt', 'w') as file:
        file.write(f'USERS\n{users}\nCONVERTATIONS\n{convertations}')

    await message.answer_document(document=FSInputFile('info.txt'))

@dp.message()
async def echo_handler(message: types.Message) -> None:
    await message.answer("Я тебя не понимаю. Отправь ссылку на видео в тикток, чтобы я смог его скачать")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
