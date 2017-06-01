# -*- coding: utf-8 -*-
import base_handler as base


class ArticlesListHandler(base.BaseHandler):

    def __init__(self, application, request, **kwargs):
        super(ArticlesListHandler, self).__init__(application, request, **kwargs)

    def get(self):
        paging = self.pre_pagination()
        error, data, paginator = self.db.get_articles(paging)
        if error:
            self.error_log("get articles from DB", error, data)
            self.write_response({'Error. See logs output.'}, 400)

        response = self.paginator(paginator, 'articles/', data)

        self.write_response(response, 200)
        return


class ArticlesUpdatedListHandler(base.BaseHandler):

    def __init__(self, application, request, **kwargs):
        super(ArticlesUpdatedListHandler, self).__init__(application, request, **kwargs)

    def get(self):
        paging = self.pre_pagination()
        error, data, paginator = self.db.get_articles(paging, status=1)
        if error:
            self.error_log("get articles from DB", error, data)
            self.write_response({'Error. See logs output.'}, 400)

        response = self.paginator(paginator, 'articles/updated/', data)

        self.write_response(response, 200)
        return


class ArticlesUpdatedHistoryListHandler(base.BaseHandler):

    def __init__(self, application, request, **kwargs):
        super(ArticlesUpdatedHistoryListHandler, self).__init__(application, request, **kwargs)

    def get(self, parent_id):
        paging = self.pre_pagination()
        error, data, paginator = self.db.get_articles(paging, parent_id=parent_id, status=0)
        if error:
            self.error_log("get articles from DB", error, data)
            self.write_response({'Error. See logs output.'}, 400)

        response = self.paginator(paginator, 'articles/updated/history/', data)

        self.write_response(response, 200)
        return


class ArticlesDeletedListHandler(base.BaseHandler):

    def __init__(self, application, request, **kwargs):
        super(ArticlesDeletedListHandler, self).__init__(application, request, **kwargs)

    def get(self):
        paging = self.pre_pagination()
        error, data, paginator = self.db.get_articles(paging, status=2)
        if error:
            self.error_log("get articles from DB", error, data)
            self.write_response({'Error. See logs output.'}, 400)

        response = self.paginator(paginator, 'articles/deleted/', data)

        self.write_response(response, 200)
        return


class ArticlesGetHandler(base.BaseHandler):

    def __init__(self, application, request, **kwargs):
        super(ArticlesGetHandler, self).__init__(application, request, **kwargs)

    def get(self, article_id):

        error, data = self.db.get_article(article_id)
        if error:
            self.error_log("get article from DB", error, data)
            self.write_response({'Error. See logs output.'}, 400)
        response = self.convert_data(data)

        self.write_response(response, 200)
        return
