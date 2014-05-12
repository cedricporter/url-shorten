#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import re
import string
import random
import urlparse

from tornado.web import HTTPError
import tornado.gen
import tornado.httpserver
import tornado.options
import tornado.web
import tornadoredis

from etc import config, const


regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def validate_url(url):
    return bool(regex.match(url))


def gen_short_id(length=config.SHORT_ID_LENGTH):
    return "".join(random.sample(string.digits + string.ascii_letters, length))


def gen_cache_key(*args):
    return ":".join(str(item) for item in args)


c = tornadoredis.Client()
c.connect()


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, short_id):
        key = gen_cache_key(const.CACHE_KEY_PREFIX.SHORT_ID, short_id)
        url = yield tornado.gen.Task(c.get, key)
        if url:
            self.redirect(url)
        else:
            raise HTTPError(404)
        self.finish()


class ShortenUrlHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        url = self.get_argument("url")
        if not validate_url(url):
            self.write("not a valid url")
            self.finish()
            return

        while True:
            key = gen_cache_key(const.CACHE_KEY_PREFIX.REVERSE_URL, url)
            short_id = yield tornado.gen.Task(c.get, key)
            if short_id:
                break
            
            short_id = gen_short_id()
            key = gen_cache_key(const.CACHE_KEY_PREFIX.SHORT_ID, short_id)
            ret = yield tornado.gen.Task(c.get, key)
            if ret:
                continue
            
            yield tornado.gen.Task(c.set, key, url)
            key = gen_cache_key(const.CACHE_KEY_PREFIX.REVERSE_URL, url)
            yield tornado.gen.Task(c.set, key, short_id)
            break

        self.write(urlparse.urljoin(config.SITE_URL, short_id))
        self.finish()

                    
application = tornado.web.Application([
    (r"/short/?", ShortenUrlHandler),
    (r"/([a-zA-Z0-9]{%s})/?" % config.SHORT_ID_LENGTH, MainHandler),
])

if __name__ == "__main__":
    application.listen(config.PORT)
    tornado.ioloop.IOLoop.instance().start()

    

