# Таблица (Python + FastAPI)

Серверная версия табличного приложения с настоящим движком формул, графом зависимостей и SQLite-хранилищем.

## Архитектура

- **FastAPI** — веб-фреймворк
- **Lark** — парсер формул с полноценной грамматикой
- **SQLite** — персистентное хранение ячеек
- **Граф зависимостей** — автоматический пересчёт при изменении ячеек
- **Обнаружение циклов** — `#CYCLE` при круговых ссылках

## Возможности

- Редактирование ячеек через браузер
- Формулы: `=A1+B2`, `=A1*2`, `=(A1+B2)/C3`
- Функции диапазона: `SUM`, `AVERAGE`, `MIN`, `MAX`, `COUNT`
- Пересчёт зависимых ячеек в реальном времени
- Сохранение в SQLite между перезапусками

## Установка

```bash
cd py-table
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Запуск

```bash
cd py-table
source venv/Scripts/activate
winpty ./venv/Scripts/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Откройте браузер: `http://localhost:8000/static/index.html`

## API

- `GET /api/sheet` — вся таблица
- `GET /api/cell/{addr}` — ячейка (например, `A1`)
- `POST /api/cell/{addr}` — установить значение/формулу
- `DELETE /api/clear` — очистить таблицу

## Структура

```
py-table/
├── main.py              # FastAPI приложение
├── requirements.txt
├── core/
│   ├── formula.py       # Lark-парсер и вычислитель
│   ├── deps.py          # Граф зависимостей (DAG)
│   ├── sheet.py         # Модель таблицы
│   └── db.py            # SQLite
└── static/
    └── index.html       # Фронтенд
```

## Пример работы в Python

```python
from core.sheet import Sheet
from core.db import Database

db = Database()
s = Sheet(db)

s.set('A1', '10')
s.set('B1', '=A1*2')      # 20.0
s.set('C1', '=SUM(A1:B1)') # 30.0

s.set('A1', '5')           # B1 и C1 пересчитаются автоматически
print(s.to_dict())
```
