import time
from random import shuffle
from os import getenv, listdir
from dotenv import load_dotenv
from telegram import Bot
from pytimeparse.timeparse import timeparse
from photo_loader import SPACEX_DIR_NAME, APOD_DIR_NAME, EPIC_DIR_NAME, get_folder_path


def parse_delay(delay):
    parsed_delay = timeparse(delay)
    if delay and parsed_delay:
        return parsed_delay
    return timeparse("24h")


def main():
    load_dotenv()
    bot = Bot(token=getenv('BOT_TOKEN'))
    content = []
    for folder_name in [SPACEX_DIR_NAME, APOD_DIR_NAME, EPIC_DIR_NAME]:
        folder_path = get_folder_path(folder_name)
        if folder_path.is_dir():
            folder_items = [folder_path / filename
                            for filename in listdir(folder_path)]
            content.extend(folder_items)
    shuffle(content)
    delay = parse_delay(getenv('DELAY'))
    channel_name = getenv('CHANNEL_NAME')
    bot.send_message(chat_id=channel_name, text=f"Задержка постинга фото: {delay} секунд")
    for photo_path in content:
        with open(photo_path, 'rb') as photo_file:
            bot.send_photo(chat_id=channel_name, photo=photo_file, timeout=300)
        time.sleep(delay)


if __name__ == "__main__":
    main()
