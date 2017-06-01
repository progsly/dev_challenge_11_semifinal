#!/usr/bin/env python

import logging

import tornado.httpserver
import tornado.ioloop
import tornado.web

import config
import handlers.parser
import handlers.articles
from database import DB


class APIService(tornado.web.Application):

    def __init__(self):
        debug = config.get('debug')

        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.ERROR)

        app_settings = {
            'debug': debug,
        }

        app_handlers = [
            (r'^/api/run_checker/?$', handlers.parser.InternalParserHandler),
            (r'^/api/articles/?$', handlers.articles.ArticlesListHandler),
            (r'^/api/articles/updated/?$', handlers.articles.ArticlesUpdatedListHandler),
            (r'^/api/articles/updated/history/(\d*)/?$', handlers.articles.ArticlesUpdatedHistoryListHandler),
            (r'^/api/articles/deleted/?$', handlers.articles.ArticlesDeletedListHandler),
            (r'^/api/articles/one/(\d*)/?$', handlers.articles.ArticlesGetHandler),
        ]

        self.database = DB()
        self.database.maybe_create_tables()

        super(APIService, self).__init__(app_handlers, **app_settings)

if __name__ == '__main__':
    port = 8000
    address = '0.0.0.0'
    logging.info('listening on %s:%d', address, port)

    ioloop = tornado.ioloop.IOLoop.instance()

    tornado.httpserver.HTTPServer(request_callback=APIService()).listen(port, address=address)

    ioloop.start()
