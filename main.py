import time
from random import shuffle
from os import getenv, listdir
from dotenv import load_dotenv
from telegram import Bot
from pytimeparse.timeparse import timeparse
from photo_loader import SPACEX_DIR_NAME, APOD_DIR_NAME, EPIC_DIR_NAME, get_folder_path


load_dotenv()

CHANNEL_NAME = "@space_telegram"


def parse_delay():
    delay = getenv("DELAY")
    if delay is None or timeparse(delay) is None:
        return timeparse("24h")
    return timeparse(delay)


def post_photo(bot, photo_path):
    bot.send_photo(chat_id=CHANNEL_NAME, photo=open(photo_path, 'rb'), timeout=300)


def post_text(bot, text):
    bot.send_message(chat_id=CHANNEL_NAME, text=text)


def main():
    bot = Bot(token=getenv('BOT_TOKEN'))
    content = []
    for folder_name in [SPACEX_DIR_NAME, APOD_DIR_NAME, EPIC_DIR_NAME]:
        folder_items = [get_folder_path(folder_name) / filename
                        for filename in listdir(get_folder_path(folder_name))]
        content.extend(folder_items)
    shuffle(content)
    delay = parse_delay()
    post_text(bot, f"Задержка постинга фото: {parse_delay()} секунд")
    for photo_path in content:
        post_photo(bot, photo_path)
        time.sleep(delay)


if __name__ == "__main__":
    main()
