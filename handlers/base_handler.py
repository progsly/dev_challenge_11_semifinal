import tornado.web
import logging
import time
import config


class BaseHandler(tornado.web.RequestHandler):
    STATUSES = {0: "no changes", 1: "updated", 2: "deleted"}

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)

    @property
    def db(self):
        return self.application.database

    def get_query_param(self, name, required=False, casttype=int, request_type="GET"):
        if request_type == "GET":
            params = self.request.arguments
            parameter = params.get(name)
            if parameter:
                parameter = parameter[0]
        else:
            params = tornado.escape.json_decode(self.request.body)
            parameter = params.get(name)

        if required and parameter is None:
            raise Exception({'message': {'error': 'Missing require parameter {}'.format(name)}, 'status': 400})

        if casttype is not None and parameter:
            parameter = casttype(parameter)

        return parameter

    def write_response(self, data, status):
        self.set_status(status)
        self.finish(data)

    @staticmethod
    def error_log(text, error, data=None):
        logging.error(text)
        logging.error(error)
        logging.error(data)
        return

    """
    get query data to pagination
    """
    def pre_pagination(self):
        limit = self.get_query_param('limit', False, int)
        before = self.get_query_param('before', False, int)
        after = self.get_query_param('after', False, int)

        if limit is None or (limit > 1000 or limit <= 0):
            limit = 20

        return {"limit": limit, "before": before, "after": after}

    """
    build Cursor-based pagination
    """
    def paginator(self,  paging, action, data, http_query=''):
        base_url = '{}/api/'.format(self.request.host)

        action = "http://{0}{1}".format(base_url, action)

        response = {"paging": {}}

        is_next = True
        is_prev = False
        if len(data) > 0:
            if paging['before'] is not None:
                is_next = True

            if paging['after'] is not None:
                is_prev = True

            if len(data) > paging['limit']:
                is_next = True
                del data[-1]
                if paging['before'] is not None:
                    is_prev = True
            else:
                if paging['before'] is None and paging['after'] is None:
                    is_next = False

            if paging['before'] is not None:
                data.reverse()

            response['paging']['cursors'] = {
                'after': data[-1]['id'],
                'before': data[0]['id']
            }

            response['paging']['next'] = '{0}?limit={1}&after={2}{3}'.format(action, paging['limit'], data[-1]['id'],
                                                                             http_query) if is_next else None

            response['paging']['previous'] = '{0}?limit={1}&before={2}{3}'.format(action, paging['limit'],
                                                                                  data[0]['id'],
                                                                                  http_query) if is_prev else None
        response['data'] = self.convert_data_list(data)

        return response

    def convert_data_list(self, data):
        new_response = []

        for item in data:
            if 'created_at' in item:
                item['created_at'] = int(time.mktime(item['created_at'].timetuple()))
            if 'updated_at' in item:
                item['updated_at'] = int(time.mktime(item['updated_at'].timetuple()))

            if 'status' in item:
                item['status'] = self.STATUSES[item['status']]

            if 'link' in item:
                item['link'] = config.get('base_url') + item['link']

            new_response.append(item)

        return new_response

    def convert_data(self, data):

        if 'created_at' in data:
            data['created_at'] = int(time.mktime(data['created_at'].timetuple()))
        if 'updated_at' in data:
            data['updated_at'] = int(time.mktime(data['updated_at'].timetuple()))

        if 'status' in data:
            data['status'] = self.STATUSES[data['status']]

        if 'link' in data:
            data['link'] = config.get('base_url') + data['link']

        return data
