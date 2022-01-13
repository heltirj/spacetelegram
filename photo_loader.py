import requests
from datetime import datetime
from os import getenv
from pathlib import Path
from shutil import rmtree
from urllib.parse import unquote, urlsplit, urlencode
from dotenv import load_dotenv


SPACEX_DIR_NAME = "spacex"
APOD_DIR_NAME = "apod"
EPIC_DIR_NAME = "epic"


def get_folder_path(folder_name):
    return Path(__file__).parent.absolute() / folder_name


def get_json(url, params=None):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def parse_img_ext(img_url):
    return Path(unquote(urlsplit(img_url).path)).suffix


def save_img(img_url, folder_name, file_name):
    folder_path = get_folder_path(folder_name)
    response = requests.get(img_url)
    response.raise_for_status()
    file_path = folder_path / f"{file_name}{parse_img_ext(img_url)}"
    with open(file_path, "wb") as image:
        image.write(response.content)


def get_spacex_image_links():
    url = "https://api.spacexdata.com/v3/launches"
    launches = get_json(url)
    for launch in reversed(launches):
        if launch["links"]["flickr_images"]:
            return launch["links"]["flickr_images"]


def fetch_spacex_last_launch(folder_path):
    links = get_spacex_image_links()
    for img_number, img_url in enumerate(links):
        save_img(img_url, folder_path, img_number)


def fetch_apod_pictures(count, nasa_api_key, folder_path):
    url = "https://api.nasa.gov/planetary/apod"
    params = {"api_key": nasa_api_key,
              "count": count}
    apods = get_json(url, params)
    links = [pic_data["url"]
             for pic_data in apods if  pic_data["media_type"] == "image"]
    for img_number, img_url in enumerate(links):
        save_img(img_url, folder_path, img_number)


def fetch_epic_pictures(count, nasa_api_key, folder_path):
    natural_url = "https://api.nasa.gov/EPIC/api/natural"
    params = {"api_key": nasa_api_key}
    epics = get_json(natural_url, params)
    epics = epics[:count] if len(epics) > count else epics
    for epic in epics:
        epic_date = datetime.fromisoformat(epic["date"])
        epic_image = epic["image"]
        year = datetime.strftime(epic_date, "%Y")
        month = datetime.strftime(epic_date, "%m")
        day = datetime.strftime(epic_date, "%d")
        img_url = f"https://api.nasa.gov/EPIC/archive/natural/{year}/{month}/{day}/" \
                  f"png/{epic_image}.png?{urlencode(params)}"
        save_img(img_url, folder_path, epic_image)


def main():
    load_dotenv()
    for folder in [SPACEX_DIR_NAME, APOD_DIR_NAME, EPIC_DIR_NAME]:
        folder_path = get_folder_path(folder)
        if folder_path.is_dir():
            rmtree(folder_path)
        Path(folder_path).mkdir(parents=True, exist_ok=True)
    nasa_api_key = getenv("NASA_API_KEY")
    fetch_spacex_last_launch(SPACEX_DIR_NAME)
    fetch_apod_pictures(50, nasa_api_key, APOD_DIR_NAME)
    fetch_epic_pictures(5, nasa_api_key, EPIC_DIR_NAME)
    print("Photos successfull loaded")


if __name__ == "__main__":
    main()
