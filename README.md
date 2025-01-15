# Крестики-Нолики с PostgreSQL

Этот проект представляет собой игру "Крестики-Нолики" с использованием графического интерфейса на Tkinter и базы данных PostgreSQL для сохранения информации о пользователях, играх и рейтингах.

## Описание

В этой игре два игрока (человек и компьютер) соревнуются за заполнение клеток игрового поля 3x3 своими знаками (X и O). Информация о пользователях и результатах игр сохраняется в базе данных PostgreSQL.

## Требования

Перед запуском проекта необходимо установить:

- Python 3.x
- PostgreSQL (с работающей базой данных)

### Установите необходимые библиотеки с помощью pip:

```
pip install psycopg2 tk
```

## Настройка базы данных

```
-- Таблица пользователей
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,                  -- Уникальный идентификатор пользователя
    username TEXT NOT NULL,                     -- Имя пользователя
    registration_date TIMESTAMP DEFAULT NOW(),  -- Дата регистрации
    last_login TIMESTAMP                        -- Дата последнего входа
);

-- Таблица игр
CREATE TABLE games (
    game_id SERIAL PRIMARY KEY,                 -- Уникальный идентификатор игры
    player_x INTEGER REFERENCES users(user_id), -- ID игрока, игравшего крестиками
    player_o INTEGER REFERENCES users(user_id), -- ID игрока, игравшего ноликами
    winner TEXT CHECK (winner IN ('X', 'O', 'Draw')), -- Победитель игры
    start_time TIMESTAMP DEFAULT NOW(),         -- Время начала игры
    end_time TIMESTAMP,                         -- Время завершения игры
    moves JSON NOT NULL                         -- Последовательность ходов в формате JSON
);

-- Таблица статистики
CREATE TABLE statistics (
    stat_id SERIAL PRIMARY KEY,                 -- Уникальный идентификатор записи
    user_id INTEGER REFERENCES users(user_id),  -- ID пользователя
    games_played INTEGER DEFAULT 0,             -- Общее количество игр
    games_won INTEGER DEFAULT 0,                -- Количество побед
    games_drawn INTEGER DEFAULT 0,              -- Количество ничьих
    games_lost INTEGER DEFAULT 0                -- Количество поражений
);

## В коде используется подключение к базе данных PostgreSQL с параметрами:
```

dbname: tic-tac-toe
user: postgres
password: ""
host: localhost
port: 2006

```

## Запуск игры
```

python TIC-TAC-TOE.py

```

```
