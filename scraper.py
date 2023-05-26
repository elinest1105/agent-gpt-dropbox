import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY", default=None)
cx = os.getenv("CX", default=None)


def search_brand(brand_name, api_key, cx):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": brand_name
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def parse_search_results(search_results):
    urls = []

    if search_results and 'items' in search_results:
        for item in search_results['items']:
            urls.append(item['link'])

    return urls
