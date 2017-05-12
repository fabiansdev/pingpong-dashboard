import tornado.web

from app.handlers import auth


url = tornado.web.URLSpec

urls = (
    url(r'/login', auth.LoginHandler, name='login'),
    url(r'/logout', auth.LogoutHandler, name='logout'),
)