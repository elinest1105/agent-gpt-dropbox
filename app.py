import requests
from bs4 import BeautifulSoup
import re
import os
import dropbox
from io import BytesIO
from urllib.parse import urljoin
from flask import Flask, flash, request, redirect, jsonify

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", default=None)
app = Flask(__name__)

@app.route('/', methods=['GET'])
def get():
    return ("hello")

@app.route('/api/v1/main', methods=['POST'])
def main():
    print("hello!")
    url = request.form['URL']
    brand = request.form['brand']
    print("url-------->", url)
    # skyrizi_url = 'https://www.skyrizi.com/'
    # brand = 'Skyrizi'

    ad_urls = find_banner_ads(url, brand)
    images = download_images(ad_urls)
    upload_to_dropbox(images, ACCESS_TOKEN)
    return("success upload")

def find_banner_ads(url, brand):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    img_tags = soup.find_all('img', alt=re.compile(brand, re.IGNORECASE))
    print("joined url", img_tags)
    return [urljoin(url, img['src']) for img in img_tags]    

def download_images(urls):
    print("urls", urls)
    images = []
    for url in urls:
        response = requests.get(url)
        image_data = BytesIO(response.content)
        images.append(image_data)
    return images

def upload_to_dropbox(images, access_token):
    dbx = dropbox.Dropbox(access_token)
    for idx, img in enumerate(images):
        file_name = f'/Skyrizi_banner_ad_{idx + 1}.jpg'
        dbx.files_upload(img.getvalue(), file_name)

if __name__ == '__main__':
    app.run()
