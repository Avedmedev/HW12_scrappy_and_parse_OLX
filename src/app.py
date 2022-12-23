import aiohttp_jinja2
import jinja2
from aiohttp import web

from src.views.auth.views import AuthHandler
from src.routes import setup_routes
from src.settings import BASE_DIR
from src.utils import postgres_ctx, mongo_ctx, setup_config
from aiohttp_security import authorized_userid

from src.views.scrappy.views import ScrappyHandler


async def current_user_ctx_processor(request):
    username = await authorized_userid(request)
    is_anonymous = not bool(username)
    return {'current_user': {'is_anonymous': is_anonymous}}


def setup_jinja(app):
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader(str(BASE_DIR / 'src' / 'templates')),
                         context_processors=[current_user_ctx_processor] )


def init_app():

    app = web.Application()

    setup_config(app)
    setup_jinja(app)
    app.cleanup_ctx.extend((postgres_ctx, mongo_ctx))

    app.router.add_static(prefix='/static/', path=f"{BASE_DIR}/src/static", name='static')

    auth = AuthHandler()
    auth.setup(app)
    setup_routes(app, auth.routes)

    scrappy = ScrappyHandler()
    scrappy.setup(app)
    setup_routes(app, scrappy.routes)

    return app
