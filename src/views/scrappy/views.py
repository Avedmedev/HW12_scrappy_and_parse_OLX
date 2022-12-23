from aiohttp import web
from aiohttp_jinja2 import template

from src.workers.async_web_scrapper import load_site_data, parse_from_dict

import pydentic

from src.workers.olx_worker import scrappy_and_parse_olx_pages


class ScrappyHandler:
    def __init__(self):
        self._mongo = None

    @property
    def mongo(self):
        return self._mongo

    def setup(self, app: web.Application):
        app.on_startup.append(self._on_connect)

    async def _on_connect(self, app: web.Application):
        self._mongo = app['db_mg']

    @property
    def routes(self):
        return self._get_routes()

    def _get_routes(self) -> list:

        return [
            ("GET", '/scrapping', self.get_url_scrappy, 'get_url'),
            ("POST", '/scrapping', self.post_url_scrappy, 'get_url'),
            ("GET", '/scrapping/olx', self.get_olx_results, 'olx_scrappy'),
            # ("POST", '/scrapping/results', self.post_results, 'res_scrappy'),
            ]

    @template('pages/scrappy/url_scrappy.html')
    async def get_url_scrappy(self, request):
        return {}

    @template('pages/scrappy/url_scrappy.html')
    async def post_url_scrappy(self, request):
        data = await request.post()
        # TODO add validation url with pydentic
        all_data = {}
        try:
            all_data = await load_site_data(data['url'])
        except Exception as err:
            # TODO add logging
            print(err)

        result = await parse_from_dict(all_data)
        if result:
            print(result)
            # TODO save result in mongo db
            location = request.app.router['get_url'].url_for()
            return web.HTTPFound(location=location)

        location = request.app.router['get_url'].url_for()
        return web.HTTPFound(location=location)

    @template('pages/scrappy/olx_scrappy.html')
    async def get_olx_results(self, request):
        await scrappy_and_parse_olx_pages(self.mongo)

        # TODO read documents from collection flats

        return {}


