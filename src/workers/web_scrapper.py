import requests
import time

from bs4 import BeautifulSoup

from url_lib import get_url_list

start_time = time.time()


def get_page_data(url: str, cat: str, page_id: int) -> str:

    # if page_id:
    #     url = sitename
    # else:
    #     url = sitename

    print(f'get url: {url}')
    response = requests.get(url)
    return str(BeautifulSoup(response.text, 'lxml'))


def load_site_data(url):
    categories_list = ["1"]
    for cat in categories_list:
        for page_id in range(1):
            text = get_page_data(url, cat, page_id)
            print(text[:2000])


if __name__ == '__main__':
    url_list = get_url_list('url_list.json')

    if url_list:
        load_site_data(url_list[0])

    end_time = time.time() - start_time

    print(f"Execution time: {end_time} seconds")
