# -*- coding: utf-8 -*-

import time
import config
import torndb

from MySQLdb import MySQLError, ProgrammingError
import subprocess


class DB(object):

    db = None

    def __init__(self):
        self.db = torndb.Connection(
            host=config.get('db_host'),
            user=config.get('db_user'),
            password=config.get('db_password'),
            database=config.get('db_name')
        )

    def maybe_create_tables(self):
        try:
            error, data = self._get("SELECT COUNT(*) from articles")
            if error:
                _, _ = self._query("""
                    CREATE TABLE IF NOT EXISTS `articles` (
                    `id` int(11) NOT NULL AUTO_INCREMENT,
                    `parent_id` int(11) NOT NULL DEFAULT '0',
                    `title` text,
                    `content` longtext,
                    `status` tinyint(4) NOT NULL DEFAULT '0',
                    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `link` varchar(255) NOT NULL,
                    `hashsum` varchar(255) DEFAULT NULL,
                    PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
                """)
            return
        except Exception:
            return

    def get_article(self, article_id):
        return self._get(
            """
            SELECT id, title, link, status, created_at, updated_at, content FROM articles WHERE id = %s
            """, int(article_id)
        )

    def get_articles(self, paging, parent_id=0, status=None):
        order_by = "ASC"
        and_sql = ""
        if paging['before'] is not None:
            order_by = "DESC"
            and_sql = " and id < {}".format(paging['before'])

        if paging["after"] is not None:
            and_sql = " and id > {}".format(paging['after'])

        status_sql = ""
        if status is not None:
            status_sql = " AND status = {} ".format(status)

        sql = """
            SELECT
                id, title, link, status, created_at, updated_at, content
            FROM
                articles
            WHERE
                parent_id = {3} {0} {4} ORDER BY id {1} LIMIT {2}
        """.format(and_sql, order_by, int((paging['limit'] + 1)), parent_id, status_sql)

        error, data = self._query(sql)
        return error, data, paging

    def get_by_link(self, link):
        return self._get(
            """
            SELECT id, content, hashsum FROM articles WHERE link = %s and parent_id = 0
            """, link
        )

    def get_by_hashsum(self, hashsum, parent_id):
        return self._get(
            """
            SELECT id, content, hashsum FROM articles WHERE hashsum = %s and parent_id = %s
            """, hashsum, parent_id
        )

    def save_page(self, link, title, content, hashsum, parent_id=0):
        error, data = self._insert(
            """
            INSERT INTO
                articles (`link`, `title`, `content`, `hashsum`, `parent_id`)
            VALUES (%s, %s, %s, %s, %s)
            """, link, title, content, hashsum, int(parent_id)
        )
        return error, data

    def update_page(self, page_id, status=0):
        error, data = self._update(
            """
            UPDATE
                articles SET status = %s, updated_at = %s
            WHERE
                id = %s
            """, int(status), time.strftime('%Y-%m-%d %H:%M:%S'), int(page_id)
        )
        return error, data

    def get_all_links(self):
        error, data = self._query(
            """
            SELECT id, link FROM articles WHERE parent_id = 0 and status < 2
            """)
        return error, data

    # ### example ###
    # ### error, data = self._query( """ SELECT * FROM Table WHERE Table.id = %s """, table_id) ###

    def _query(self, query, *args, **kwargs):
        try:
            return 0, self.db.query(query, *args, **kwargs)
        except MySQLError as error:
            return error.args

    def _execute_rowcount(self, query, *args, **kwargs):
        try:
            return 0, self.db.execute_rowcount(query, *args, **kwargs)
        except MySQLError as error:
            return error.args

    def _get(self, query, *args, **kwargs):
        try:
            return 0, self.db.get(query, *args, **kwargs)
        except MySQLError as error:
            return error.args

    def _insert(self, query, *args, **kwargs):
        try:
            return 0, self.db.insert(query, *args, **kwargs)
        except MySQLError as error:
            return error.args

    def _update(self, query, *args, **kwargs):
        try:
            return 0, self.db.update(query, *args, **kwargs)
        except MySQLError as error:
            return error.args

    def execute(self, query, params=None):
        # Get data from db
        try:
            response = self.db.query(query, *params)
            if response:
                return 0, response
            else:
                return 1, ''
        except MySQLError, error:
            return error.args
