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


c = tornadoredis.Client()
c.connect()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect(config.MAIN_PAGE_REDIRECT)

                
class ExpandUrlHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, short_id):
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
        url = self.get_argument("url")
        if not util.validate_url(url):
            self.write("not a valid url")
            self.finish()
            return

        while True:
            key = util.gen_cache_key(const.CACHE_KEY_PREFIX.REVERSE_URL, url)
            short_id = yield tornado.gen.Task(c.get, key)
            if short_id:
                break
            
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

    

