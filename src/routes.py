from aiohttp import web


def setup_routes(app: web.Application, routes):
    for route in routes:
        app.router.add_route(route[0], route[1], route[2], name=route[3])
