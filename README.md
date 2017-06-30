# Monitoring system for changes in news texts

__[Task - PDF file ](back-endstandardsemi-finaltaskdevchallenge11.pdf)__ - Ukrainian language


_News feed `http://brovary-rada.gov.ua/documents/`_

To start the application, you need to run the command: __`docker-compose up`__

Ports `8000` and `3306` should be free..

### Run news parser
#### GET _http://0.0.0.0:8000/api/run_checker_
Optional parameter __`page_limit`__ (int), number of pages to scan (starting with the newest news).
By default, it scans all pages.

##### Example

* Request
```bash
$ curl -X GET
    http://0.0.0.0:8000/api/run_checker?page_limit=3
```

* Response

HTTP/1.1 200
```json
{"status": "ok"}
```

* Error Response

HTTP/1.1 500
```json
{"status": "Parsing error. See logs output."}
```


### Get news list
#### GET _http://0.0.0.0:8000/api/articles/_
Optional parameters (for pagination):

* __`limit`__ (int), Number of news in response. (Default = 20)

* __`after`__ (int), From which element to show next news

* __`before`__ (int), To what element to show news


##### Example

* Request
```bash
$ curl -X GET
    http://0.0.0.0:8000/api/articles/?limit=10
```

* Response

HTTP/1.1 200
```json
{
  "paging": {
    "previous": "http://0.0.0.0:8000/api/articles/?limit=3&before=4",
    "cursors": {
      "after": 6,
      "before": 4
    },
    "next": "http://0.0.0.0:8000/api/articles/?limit=3&after=6"
  },
   "data": [
        {
          "status": "no changes | updated | deleted",
          "title": "Page title",
          "created_at": 1496241466,
          "updated_at": 1496241466,
          "content": "html content",
          "link": "http://brovary-rada.gov.ua/documents/27297.html",
          "id": 4
        }
    ]
}
```
To go to the next or previous page, you can use
__`paging->previous`__ or __`paging->next`__

* Error Response

HTTP/1.1 400
```json
{"status": "Error. See logs output."}
```

### Get a list of changed news
#### GET _http://0.0.0.0:8000/api/articles/updated/_

The same parameters and the response as __Get news list__


### Get a history of news updates by ID
#### GET _http://0.0.0.0:8000/api/articles/updated/history/:NEWS_ID_

The same parameters and the response as __Get news list__

### Get deleted news list
#### GET _http://0.0.0.0:8000/api/articles/deleted/_

The same parameters and the response as __Get news list__

### Get one news by ID
#### GET _http://0.0.0.0:8000/api/articles/one/:NEWS_ID_

##### Example

* Request
```bash
$ curl -X GET
    http://0.0.0.0:8000/api/articles/one/1
```

* Response

HTTP/1.1 200
```json
{
    "status": "no changes | updated | deleted",
    "title": "Page title",
    "created_at": 1496241466,
    "updated_at": 1496241466,
    "content": "html content",
    "link": "http://brovary-rada.gov.ua/documents/27297.html",
    "id": 1

}
```

* Error Response

HTTP/1.1 400
```json
{"status": "Error. See logs output."}
```

### Technologies
* To implement the task has been used __Tornado Web Server__

* Database __MySQL__

* Parsing `html` pages - Python lib __Beautiful Soup__

Each saved news has 3 statuses(`no changes`, `updated`, `deleted`).
Each time you start the parser (`/api/run_checker`), compare checksum content,
If there is a difference - a new version of the document is saved, and the parent changes the status to `updated`.
When a deleted document is detected, the saved status changes to `deleted`.

The parsing function is recursive, works until it loads the specified number of pages, and if this option is not specified, until it scans all the news.
