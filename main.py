import requests
from os import getenv
from pathlib import Path
from urllib.parse import urlsplit, unquote
from dotenv import load_dotenv

load_dotenv()

SPACEX_DIR_NAME = "spacex"
APOD_DIR_NAME = "apod"
EPIC_DIR_NAME = "epic"


def get_json_data(url, params=None):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def parse_img_ext(img_url):
    return Path(unquote(urlsplit(img_url).path)).suffix


def save_img(img_url, folder_name, file_name):
    folder_path = Path(__file__).parent.absolute() / folder_name
    Path(folder_path).mkdir(parents=True, exist_ok=True)
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
             for pic_data in data if "url" in pic_data]
    for img_number, img_url in enumerate(links):
        save_img(img_url, APOD_DIR_NAME, img_number)


def main():
    fetch_spacex_last_launch()
    fetch_apod_pictures(50)


if __name__ == "__main__":
    main()
