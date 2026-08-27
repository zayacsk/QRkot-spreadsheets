# QRkot-spreadsheets

## Автор
* ФИО: Анохин Денис
* Контакты: [Telegram](https://t.me/zayac_d) | [GitHub](https://github.com/zayacsk)

## О проекте
Веб-сервис благотворительного фонда поддержки котиков на FastAPI. Позволяет управлять благотворительными проектами, пожертвованиями и пользователями через REST API. Реализовано автоматическое распределение пожертвований между проектами и формирование Excel-отчётов по завершённым проектам с загрузкой на Яндекс Диск.

## Стек технологий
* Python
* FastAPI
* FastAPIUsers
* SQLAlchemy
* Alembic
* SQLite
* xlsxwriter

## Как запустить
Клонировать репозиторий и перейти в него:

```bash
git clone https://github.com/zayacsk/cat-charity-2.git
cd cat-charity-2
```

Создать и активировать виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

Применить миграции:

```bash
alembic upgrade head
```

Запустить сервер:

```bash
uvicorn app.main:app --reload
```

После запуска API, документация будет доступна по адресу:

[Swagger](http://127.0.0.1:8000/docs)
[ReDoc](http://127.0.0.1:8000/redoc)
