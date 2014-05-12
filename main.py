#!/usr/bin/env python
# -*- coding: utf-8 -*-
# By Hua Liang[Stupid ET]

import urlparse

import tornado.options
from tornado.options import define, options
from tornado.web import HTTPError
import tornado.gen
import tornado.httpserver
import tornado.options
import tornado.web
import tornadoredis

from etc import config, const
from base import util

define("port", default=config.PORT, help="run on the given port", type=int)

CONNECTION_POOL = tornadoredis.ConnectionPool(max_connections=10,
                                              wait_for_available=True)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/short.html")
        # self.redirect(config.MAIN_PAGE_REDIRECT)


class ExpandUrlHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, short_id):
        c = tornadoredis.Client(connection_pool=CONNECTION_POOL)
        key = util.gen_cache_key(const.CACHE_KEY_PREFIX.SHORT_ID, short_id)
        url = yield tornado.gen.Task(c.get, key)
        if url:
            self.redirect(url)
        else:
            raise HTTPError(404)


class ShortenUrlHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        c = tornadoredis.Client(connection_pool=CONNECTION_POOL)
        url = self.get_argument("url")
        if not util.validate_url(url):
            self.write("not a valid url")
            self.finish()
            return
        
        key = util.gen_cache_key(const.CACHE_KEY_PREFIX.REVERSE_URL, url)
        short_id = redis_short_id = yield tornado.gen.Task(c.get, key)

        while not redis_short_id:
            short_id = util.gen_short_id()
            key = util.gen_cache_key(const.CACHE_KEY_PREFIX.SHORT_ID, short_id)
            ret = yield tornado.gen.Task(c.get, key)
            if ret:
                continue

            yield tornado.gen.Task(c.set, key, url)
            key = util.gen_cache_key(const.CACHE_KEY_PREFIX.REVERSE_URL, url)
            yield tornado.gen.Task(c.set, key, short_id)
            break

        self.write(urlparse.urljoin(config.SITE_URL, short_id))
        self.finish()


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/short/?", ShortenUrlHandler),
    (r"/([a-zA-Z0-9]{%s})/?" % config.SHORT_ID_LENGTH, ExpandUrlHandler),
], debug=config.DEBUG)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
