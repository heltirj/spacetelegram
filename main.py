import requests
import time
from random import shuffle
from os import getenv, listdir
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, unquote, urlencode
from dotenv import load_dotenv
from telegram import Bot
from pytimeparse.timeparse import timeparse


load_dotenv()

SPACEX_DIR_NAME = "spacex"
APOD_DIR_NAME = "apod"
EPIC_DIR_NAME = "epic"
CHANNEL_NAME = "@space_telegram"


def get_folder_path(folder_name):
    folder_path = Path(__file__).parent.absolute() / folder_name
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    return folder_path


def get_json_data(url, params=None):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def parse_img_ext(img_url):
    return Path(unquote(urlsplit(img_url).path)).suffix


def parse_delay():
    delay = getenv("DELAY")
    if delay is None or timeparse(delay) is None:
        return timeparse("24h")
    return timeparse(delay)


def save_img(img_url, folder_name, file_name):
    folder_path = get_folder_path(folder_name)
    response = requests.get(img_url)
    response.raise_for_status()
    file_path = folder_path / f"{file_name}{parse_img_ext(img_url)}"
    with open(file_path, "wb") as image:
        image.write(response.content)


def get_spacex_image_links():
    url = "https://api.spacexdata.com/v3/launches"
    launches = get_json_data(url)
    for launch in reversed(launches):
        if len(launch["links"]["flickr_images"]) != 0:
            return launch["links"]["flickr_images"]


def fetch_spacex_last_launch():
    links = get_spacex_image_links()
    for img_number, img_url in enumerate(links):
        save_img(img_url, SPACEX_DIR_NAME, img_number)


def fetch_apod_pictures(count):
    url = "https://api.nasa.gov/planetary/apod"
    params = {"api_key": getenv("NASA_API_KEY"),
              "count": count}
    data = get_json_data(url, params)
    links = [pic_data["url"]
             for pic_data in data if  pic_data["media_type"] == "image"]
    for img_number, img_url in enumerate(links):
        save_img(img_url, APOD_DIR_NAME, img_number)


def fetch_epic_pictures(count):
    natural_url = "https://api.nasa.gov/EPIC/api/natural"
    params = {"api_key": getenv("NASA_API_KEY")}
    epics = get_json_data(natural_url, params)
    epics = epics[:count] if len(epics) > count else epics
    for epic in epics:
        epic_date = datetime.fromisoformat(epic["date"])
        epic_image = epic["image"]
        img_url = f"https://api.nasa.gov/EPIC/archive/natural/{epic_date.year}/{epic_date.month}/{epic_date.day}/" \
                  f"png/{epic_image}.png?{urlencode(params)}"
        save_img(img_url, EPIC_DIR_NAME, epic_image)


def post_photo(bot, photo_path):
    bot.send_photo(chat_id=CHANNEL_NAME, photo=open(photo_path, 'rb'), timeout=300)


def post_delay(bot):
    bot.send_message(chat_id=CHANNEL_NAME, text=f"Задержка постинга фото: {parse_delay()} секунд")


def main():
    content = []
    for folder_name in [SPACEX_DIR_NAME, APOD_DIR_NAME, EPIC_DIR_NAME]:
        folder_items = [get_folder_path(folder_name) / filename
                        for filename in listdir(get_folder_path(folder_name))]
        content.extend(folder_items)
    shuffle(content)
    bot = Bot(token=getenv('BOT_TOKEN'))
    delay = parse_delay()
    post_delay(bot)
    for photo_path in content:
        post_photo(bot, photo_path)
        time.sleep(delay)


if __name__ == "__main__":
    main()
