import requests
from bs4 import BeautifulSoup
import re
import os
import dropbox
import base64
from io import BytesIO
from urllib.parse import urljoin
from flask import Flask, request
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
import datetime
from scraper import *

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY", default=None)
cx = os.getenv("CX", default=None)

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)


@app.route('/', methods=['GET'])
@cross_origin()
def get():
    return ("hello")


@app.route('/api/v1/main', methods=['POST'])
@cross_origin()
def main():
    req_data = request.get_json()

    brand = req_data["brand"]
    dropkey = req_data["apikey"]
    ad_urls = []
    images = []

    search_results = search_brand(brand, api_key, cx)
    parsed_urls = parse_search_results(search_results)

    for result in parsed_urls:
        ad_urls.append(find_banner_ads(result, brand))

    for url in ad_urls:
        images.append(download_images(url))

    for image in images:
        upload_to_dropbox(brand, image, dropkey)
    return ("Upload Success!")

def find_banner_ads(url, brand):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    img_tags = soup.find_all('img', alt=re.compile(brand, re.IGNORECASE))
    return [urljoin(url, img['src']) for img in img_tags if 'src' in img.attrs]


def download_images(urls):
    images = []
    for url in urls:
        if url.startswith('data:image/'):
            img_data = url.split(',', 1)[1]
            image_data = BytesIO(base64.b64decode(img_data))
        else:
            response = requests.get(url)
            image_data = BytesIO(response.content)
        images.append(image_data)
    return images


def upload_to_dropbox(brand, image, access_token):
    dbx = dropbox.Dropbox(access_token)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    for idx, img in enumerate(image):
        file_name = f'/banner_ads/{brand}_banner_ad_{timestamp}_{idx + 1}.jpg'
        dbx.files_upload(img.getvalue(), file_name,
                        mode=dropbox.files.WriteMode.overwrite)


if __name__ == '__main__':
    app.run()
