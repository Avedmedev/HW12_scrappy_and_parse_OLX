import asyncio
import sys

from aiohttp import web

from src.app import init_app


def main():
    app = init_app()
    config = app['config']['app']
    web.run_app(app, host=config['host'], port=config['port'])


if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    main()
