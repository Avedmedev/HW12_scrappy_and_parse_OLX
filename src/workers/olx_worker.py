import asyncio
import json
import os
from pathlib import Path
from asyncio import Queue
import logging

import aiohttp
from bs4 import BeautifulSoup
from bson import ObjectId


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] - %(name)s - %(funcName)s(%(lineno)d) - %(message)s')


def get_url_dict(filename: Path) -> dict:
    logging.info(filename)
    with open(filename) as fp:
        url_list = json.load(fp)
    return url_list.get('urls').get('https://www.olx.ua')


url_data = get_url_dict(Path(__file__).parent / 'url_dict.json')


all_pages = {}


async def get_pages_count(page: BeautifulSoup) -> int:
    el_quotes = url_data['pages_quote']
    pagination_quote = page.find_all(el_quotes['tag'], attrs=el_quotes['attrs'])  # проверить как работает этот параметр
    pages = [quote.text for quote in pagination_quote]
    pages_count = max(map(int, (filter(str.isdigit, pages))))

    logging.info(f"{pages_count} pages found")

    return pages_count


async def produce_page_data(session, url: str, q_pages: Queue):
    async with session.get(url) as resp:
        assert resp.status == 200
        logging.info(url)
        resp_text = BeautifulSoup(await resp.text(), 'html.parser')
        all_pages[url] = resp_text
        await q_pages.put((url, resp_text))
        return resp_text


async def insert_data(collection, data_list):
    flats = []

    for data in data_list:
        flats.append({
            '_id': ObjectId(),
            'title': data[0].text,
            'price': data[1].text,
            'location': data[2].text,
            'square': data[3].text[len(data[2].text):]
        })

    values = await collection.insert_many(flats)
    return values


async def parse_data(page: BeautifulSoup, mongo):

    data = {}
    for el_name, el_quotes in url_data['data'].items():
        data[el_name] = page.find_all(el_quotes['tag'], class_=el_quotes['class_'])

    data_list = list(zip(*data.values()))

    await insert_data(mongo.flats, data_list)


async def consume_page_to_mongo(q_pages: Queue, mongo):
    while True:
        url, page = await q_pages.get()
        await parse_data(page, mongo)
        q_pages.task_done()


async def scrappy_and_parse_olx_pages(mongo):
    url = url_data['url']
    async with aiohttp.ClientSession() as session:
        q_pages = Queue()

        first_page_url = url.format('')
        first_page: BeautifulSoup = await produce_page_data(session, first_page_url, q_pages)
        pages_count = await get_pages_count(first_page)

        producers = []
        for page_id in range(2, pages_count + 1):
            page_url = url.format(f"&page={page_id}")
            producer = asyncio.create_task(produce_page_data(session, page_url, q_pages))
            producers.append(producer)
        logging.info(os.cpu_count())
        consumers = [asyncio.create_task(consume_page_to_mongo(q_pages, mongo)) for _ in range(os.cpu_count())]
        await asyncio.gather(*producers)
        await q_pages.join()
        for c in consumers:
            c.cancel()
