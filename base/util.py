#!/usr/bin/env python
# -*- coding: utf-8 -*-
# By Hua Liang[Stupid ET]

import re
import string
import random
from etc import config


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

