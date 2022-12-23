from aiohttp_jinja2 import template
from aiohttp import web

from aiohttp_session import get_session
from aiohttp_security import setup as setup_security
from aiohttp_security import CookiesIdentityPolicy, authorized_userid, remember, forget
from sqlalchemy import select

from src.repository.postgres.models import User
from src.security import AuthorizationPolicy, generate_password_hash, check_password_hash


class AuthHandler:

    def __init__(self):
        self._postgres = None

    @property
    def postgres(self):
        return self._postgres

    def setup(self, app: web.Application):
        app.on_startup.append(self._on_connect)

    async def _on_connect(self, app: web.Application):
        self._postgres = app['db_pg']
        setup_security(app, CookiesIdentityPolicy(), AuthorizationPolicy(self._postgres))

    @property
    def routes(self):
        return self._get_routes()

    def _get_routes(self) -> list:
        return [
            ("GET", '/', self.index, 'index'),
            ("GET", '/signin', self.get_signin, 'signin'),
            ("POST", '/signin', self.post_signin, 'post_signin'),
            ("GET", '/login', self.get_login, 'login'),
            ("POST", '/login', self.post_login, 'post_login'),
            ("GET", '/logout', self.get_logout, 'get_logout'),
        ]

    @template('pages/index.html')
    async def index(self, request):
        return {"title": "Web Scrapper"}

    @template('pages/signin.html')
    async def get_signin(self, request):
        return {'title': "Web Scrapper"}

    @template('pages/signin.html')
    async def post_signin(self, request):
        data = await request.post()
        # TODO add validation with pydentic
        async with self.postgres as session:
            user = User(email=data['email'],
                        password=generate_password_hash(data["password"]),
                        login=data['login'])
            try:
                session.add(user)
                await session.commit()
            except Exception as err:
                # TODO add logging
                print(err)
        location = request.app.router['login'].url_for()
        raise web.HTTPFound(location=location)

    @template('pages/login.html')
    async def get_login(self, request):
        return {'title': "Web Scrapper"}

    @template('pages/login.html')
    async def post_login(self, request):
        data = await request.post()
        # TODO add validation with pydentic
        async with self.postgres as session:
            r = await session.execute(select(User).filter(User.email == data['email']))
            user = r.scalars().first()
        if user and check_password_hash(user.password, data["password"]):
            location = request.app.router['get_url'].url_for()
            response = web.HTTPFound(location=location)
            # TODO encrypt {user.id : user.login}
            await remember(request, response, str(user.login))
            return response
        else:
            return web.HTTPFound(location=request.app.router['login'].url_for())

    @template('pages/login.html')
    async def get_logout(self, request):
        user_id = await authorized_userid(request)
        if user_id:
            response = web.HTTPFound(location=request.app.router['login'].url_for())
            await forget(request, response)
            return response
        return web.HTTPForbidden(text='go away')
