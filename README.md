# Систему моніторингу за змінами у текстах новин


_Стрічка новин `http://brovary-rada.gov.ua/documents/`_

Для старту додатка необхідно запустити команда: __`docker-compose up`__


### Запуск парсера новин
#### GET _http://0.0.0.0:8000/api/run_checker_
Необов’язковий параметр __`page_limit`__ (int), кількість сторінок для сканування (починає з новіших новин).
За замовчуваням сканує всі сторінки.

##### Приклад

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


### Отримати список новин
#### GET _http://0.0.0.0:8000/api/articles/_
Необов’язкові параметри (для пагінації):

* __`limit`__ (int), кількість новин у видачі (За замовчуваням = 20)

* __`after`__ (int), від якого елементу показувати наступні новини

* __`before`__ (int), до якого елементу показувати новини


##### Приклад

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
        }, ...
    ]
}
```
Для переходу на наступну або попередню сторінку можна використовувати
__`paging->previous`__ або __`paging->next`__

* Error Response

HTTP/1.1 400
```json
{"status": "Error. See logs output."}
```

### Отримати список змінених новин
#### GET _http://0.0.0.0:8000/api/articles/updated/_

Ті ж самі параметри та відповідь як у __Отримати список новин__


### Отримати історію змін новини по ID новини
#### GET _http://0.0.0.0:8000/api/articles/updated/history/:NEWS_ID_

Ті ж самі параметри та відповідь як у __Отримати список новин__

### Отримати список видалених новини
#### GET _http://0.0.0.0:8000/api/articles/deleted/_

Ті ж самі параметри та відповідь як у __Отримати список новин__

### Отримати одну новину по ID
#### GET _http://0.0.0.0:8000/api/articles/one/:NEWS_ID_

##### Приклад

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

### Технології
* Для реалізації завдання був використан __Tornado Web Server__

* База даних __MySQL__

* Прасинг `html` сторінок - Python бібліотека __Beautiful Soup__

Кожна збережена новина має 3 статуси (`no changes`, `updated`, `deleted`).
При кожному наступному запуску парсера (`/api/run_checker`), порівнюються чексуми контенту,
якщо є різниця - зберігається нова версія документу, а у батьківського змінюється статус на `updated`.
При виявлені видаленого документу - статус збереженого змінюється на `deleted`.

Функція парсингу рекурсина, працює до поки не завантажить вказану кількість сторінок, а якщо цей параметр не вказан, поки не просканує всі новини.
