import time
from random import shuffle
from os import getenv, listdir
from dotenv import load_dotenv
from telegram import Bot
from pytimeparse.timeparse import timeparse
from photo_loader import SPACEX_DIR_NAME, APOD_DIR_NAME, EPIC_DIR_NAME, get_folder_path

def parse_delay(str_delay):
    if str_delay and timeparse(str_delay):
        return timeparse(str_delay)
    return timeparse("24h")


def main():
    load_dotenv()
    bot = Bot(token=getenv('BOT_TOKEN'))
    content = []
    for folder_name in [SPACEX_DIR_NAME, APOD_DIR_NAME, EPIC_DIR_NAME]:
        if get_folder_path(folder_name).is_dir():
            folder_items = [get_folder_path(folder_name) / filename
                        for filename in listdir(get_folder_path(folder_name))]
            content.extend(folder_items)
    shuffle(content)
    delay = parse_delay(getenv('DELAY'))
    channel_name = getenv('CHANNEL_NAME')
    bot.send_message(chat_id=channel_name,  text=f"Задержка постинга фото: {delay} секунд")
    for photo_path in content:
        with open(photo_path, 'rb') as photo_file:
            bot.send_photo(chat_id=channel_name, photo=photo_file, timeout=300)
        time.sleep(delay)


if __name__ == "__main__":
    main()
