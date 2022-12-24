import logging

from aiohttp import web
from aiohttp_jinja2 import template

from src.repository.mongo.olx_flats import get_all_flats
from src.security import auth_required
from src.workers.async_web_scrapper import load_site_data, parse_from_dict

import pydentic

from src.workers.olx_worker import scrappy_and_parse_olx_pages


# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s [%(levelname)s] - %(name)s - %(funcName)s(%(lineno)d) - %(message)s'
# )
#

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

    @auth_required
    @template('pages/scrappy/url_scrappy.html')
    async def get_url_scrappy(self, request):
        return {}

    @auth_required
    @template('pages/scrappy/url_scrappy.html')
    async def post_url_scrappy(self, request):
        data = await request.post()
        # TODO add validation url with pydentic
        all_data = {}
        try:
            all_data = await load_site_data(data['url_name'])
        except Exception as err:
            logging.error(err)

        result = await parse_from_dict(all_data)

        logging.info(result)

        if result:
            return {'url_name': data['url_name'], 'result': result.get(data['url_name'])}

        location = request.app.router['get_url'].url_for()
        return web.HTTPFound(location=location)

    @auth_required
    @template('pages/scrappy/olx_scrappy.html')
    async def get_olx_results(self, request):
        await scrappy_and_parse_olx_pages(self.mongo)

        flats = await get_all_flats(self.mongo)

        return {"flats": flats}


