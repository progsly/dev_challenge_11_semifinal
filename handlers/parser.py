# -*- coding: utf-8 -*-
import requests
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

import base_handler as base
import logging
import config
import hashlib


class InternalParserHandler(base.BaseHandler):
    all_pages = []

    def __init__(self, application, request, **kwargs):
        super(InternalParserHandler, self).__init__(application, request, **kwargs)

    def get(self):
        page_limit = self.get_query_param("page_limit", required=False, casttype=int)
        if page_limit is None:
            # parse all pages
            page_limit = 0

        logging.info("page limit %s" % page_limit)

        status = True
        if self.process(config.get('doc_patch'), page_limit=page_limit):
            error, data = self.db.get_all_links()
            if error:
                self.error_log("get all links from DB", error, data)
                status = False

            if data and not error:
                for item in data:
                    # check if link deleted from site
                    if item['link'] not in self.all_pages:
                        error, data = self.db.update_page(item['id'], status=2)
                        if error:
                            self.error_log("update_page", error, data)
                            status = False
        else:
            status = False

        response = {'status': 'ok' if status else 'Parsing error. See logs output.'}
        code = 200 if status else 500
        self.write_response(response, code)
        return

    """
    Recursive process
    """
    def process(self, doc_patch, current_page=1, page_limit=0):
        if page_limit and (current_page > page_limit):
            return True
        response = requests.get(config.get('base_url') + doc_patch)
        if response.status_code is not 200:
            return False

        page_content = BeautifulSoup(response.content)

        links = page_content.select(".bg2-content div.bg1-content a")
        next_group = next_page = None

        for link in links:
            if len(link.attrs) == 1:
                if unicode(link.text) != u'»»' and unicode(link.text) != u'««':
                    self.all_pages.append(link.attrs['href'])
                    if not self.process_page(link.attrs['href'], link.text):
                        break
                    else:
                        continue
                if unicode(link.text) == u'»»':
                    next_group = link.attrs['href']

            if len(link.attrs) == 2:
                if unicode(link.text) == str(current_page + 1):
                    next_page = link.attrs['href']
                    break

        current_page += 1
        if next_page is not None:
            self.process(next_page, current_page, page_limit)
        elif next_group is not None:
            self.process(next_group, current_page, page_limit)

        return True

    """
    Save or update pages in db
    """
    def process_page(self, link, title):
        response = requests.get(config.get('base_url') + link)
        if response.status_code is not 200:
            return False

        error, data = self.db.get_by_link(link)
        if error:
            self.error_log("get_by_link", error, data)
            return False

        content = response.content
        content_hashsum = self.get_hashsum(content)

        if not data:
            error, data = self.db.save_page(link, title, content, hashsum=content_hashsum)
            if error:
                self.error_log("save_page", error, data)
                return False

        else:
            if self.get_hashsum(data['content'].encode('utf8')) == content_hashsum:
                return True

            parent_id = data['id']
            error, data = self.db.get_by_hashsum(content_hashsum, parent_id)
            if error:
                self.error_log("get_by_hashsum", error, data)
                return False

            if data:
                return True

            error, data = self.db.save_page(link, title, content, hashsum=content_hashsum, parent_id=parent_id)
            if error:
                self.error_log("save_page with parent", error, data)
                return False

            error, data = self.db.update_page(parent_id, status=1)
            if error:
                self.error_log("update_page", error, data)
                return False

        return True

    @staticmethod
    def get_hashsum(content):
        md5 = hashlib.md5()
        md5.update(content)
        return md5.hexdigest()
