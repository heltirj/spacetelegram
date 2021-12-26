import requests
from os import getenv
from pathlib import Path
from urllib.parse import urlsplit, unquote


def parse_img_ext(img_url):
  return  Path(unquote(urlsplit(img_url).path)).suffix
    

def save_img(img_url, img_path):
  response = requests.get(img_url)
  response.raise_for_status()
  with open(img_path, "wb") as image:
    image.write(response.content)


def get_spacex_image_links():
  url = "https://api.spacexdata.com/v3/launches"
  response = requests.get(url)
  response.raise_for_status()
  launches = response.json()
  links, flickr_images = "links", "flickr_images"
  for launch in reversed(launches):
    if len(launch[links][flickr_images]) != 0:
      return launch[links][flickr_images]


def fetch_spacex_last_launch(img_folder_path):
  links = get_spacex_image_links()
  for img_number, img_url  in enumerate(links):
     save_img(img_url, img_folder_path / f"{img_number}.jpg")


def fetch_nasa_pictures(count, img_folder_path):
  url = "https://api.nasa.gov/planetary/apod"
  params = {"api_key": getenv("NASA_API_KEY"), 
            "count": count}
  response = requests.get(url, params=params)
  response.raise_for_status()
  data = response.json()
  print(data[0])
  links = [pic_data["url"] 
           for pic_data in data if "url" in pic_data]
  
  for img_number, img_url  in enumerate(links):
     print(img_url)
     save_img(img_url, img_folder_path / f"{img_number}{parse_img_ext(img_url)}")
  

def main():
  img_folder_path = Path( __file__ ).parent.absolute() / "images"
  Path(img_folder_path).mkdir(parents=True, exist_ok=True)
  fetch_spacex_last_launch(img_folder_path)
  

if __name__ == "__main__":
  # main()
  print(parse_img_ext("https://example.com/txt/hello%20world.txt?v=9#python"))
  img_folder_path = Path( __file__ ).parent.absolute() / "nasa_pics"
  Path(img_folder_path).mkdir(parents=True, exist_ok=True)
  fetch_nasa_pictures(50, img_folder_path)