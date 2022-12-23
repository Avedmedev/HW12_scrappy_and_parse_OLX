import asyncio

import aiohttp
import time
from bs4 import BeautifulSoup

from .url_lib import get_url_dict

start_time = time.time()
all_data = {}


async def get_page_data(session, url: str):
    async with session.get(url) as resp:
        assert resp.status == 200
        resp_text = BeautifulSoup(await resp.text(), 'html.parser')
        all_data[url] = resp_text


async def load_site_data(url) -> dict:
    categories_list = ["1"]
    async with aiohttp.ClientSession() as session:
        tasks = []
        for cat in categories_list:
            for page_id in range(1):
                task = asyncio.create_task(get_page_data(session, url))
                tasks.append(task)
        await asyncio.gather(*tasks)
    return all_data


async def get_data_from_soup(soup: BeautifulSoup):
    data = {}
    quotes = soup.find_all('body')

    # el_quotes = {"tag": "li", "attrs": {"data-testid": "pagination-list-item"}}
    # quotes = soup.find_all(el_quotes['tag'], attrs=el_quotes['attrs'])  # проверить как работает этот параметр

    for quote in quotes:
        data[quote] = quote.text
    return data


async def parse_from_dict(data: dict):
    parsed_data = {}
    for key, soup in data.items():
        parsed_data[key] = await get_data_from_soup(soup)

    return parsed_data


async def get_data_from_soup_by_dict(url_data: dict):
    soup = all_data[url_data['url']]
    data = {}
    for el_name, el_quotes in url_data['data'].items():
        data[el_name] = soup.find_all(el_quotes['tag'], class_=el_quotes['class_'])
    print(*data.keys(), sep='\t')
    print(*[[el.text for el in data] for data in zip(*data.values())], sep='\n')


if __name__ == '__main__':

    url_dict = get_url_dict('url_dict.json')

    if url_dict:
        for site_name, url_data in url_dict.items():
            asyncio.run(load_site_data(url_data['url']))
            asyncio.run(get_data_from_soup_by_dict(url_data))

    end_time = time.time() - start_time

    print(f"Execution time: {end_time} seconds")
