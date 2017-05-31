import sys
import logging


CONFIGURATION = {
    "debug": True,
    "db_host": "mysql:3306",
    "db_user": "root",
    "db_password": "root",
    "db_name": "devchallenge_11_2",
    "base_url": "http://brovary-rada.gov.ua",
    "doc_patch": "/documents/"

}


def get(key, default=None):
    if key in CONFIGURATION:
        return CONFIGURATION[key]

    if default:
        return default

    logging.fatal("No setting for %s found in config.py" % key)
    sys.exit(1)
