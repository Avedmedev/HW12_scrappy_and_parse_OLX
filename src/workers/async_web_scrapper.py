import asyncio

import aiohttp
import time
from bs4 import BeautifulSoup

all_data = {}


async def get_page_data(session, url: str):
    async with session.get(url) as resp:
        assert resp.status == 200
        resp_text = BeautifulSoup(await resp.text(), 'html.parser')
        all_data[url] = resp_text


async def load_site_data(url) -> dict:
    async with aiohttp.ClientSession() as session:
        task = asyncio.create_task(get_page_data(session, url))
        await asyncio.gather(task)
    return all_data


async def get_data_from_soup(soup: BeautifulSoup):
    data = []
    quotes = soup.body.find_all()

    for quote in quotes:
        data.append((quote.name, repr(quote.attrs.items()), quote.text))
    return data


async def parse_from_dict(data: dict):
    parsed_data = {}
    for key, soup in data.items():
        parsed_data[key] = await get_data_from_soup(soup)

    return parsed_data
