import asyncio

import aiohttp


async def main(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            print(await resp.text())


if __name__ == '__main__':

    url = 'http://127.0.0.1:8090'

    asyncio.run(main(url))
