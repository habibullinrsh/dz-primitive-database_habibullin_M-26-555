## Управление таблицами

[![asciinema](https://asciinema.org/a/2SdGOVbUBcYIzVxI.svg)](https://asciinema.org/a/2SdGOVbUBcYIzVxI)

### Команды

| Команда | Описание |
|---------|----------|
| `create_table <имя> <столбец1:тип> <столбец2:тип> ...` | Создать таблицу |
| `list_tables` | Показать список всех таблиц |
| `drop_table <имя_таблицы>` | Удалить таблицу |
| `exit` | Выход из программы |
| `help` | Справочная информация |

### Поддерживаемые типы данных

- `int`
- `str`
- `bool`

### Пример использования

```bash
$ database

***База данных***

>>> Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

>>> Введите команду: list_tables
- users

>>> Введите команду: drop_table users
Таблица "users" успешно удалена.

## CRUD-операции

[![asciinema](https://asciinema.org/a/gUvm58jVEEszE70u.svg)](https://asciinema.org/a/gUvm58jVEEszE70u)

### Команды

| Команда | Описание |
|---------|----------|
| `insert into <имя_таблицы> values (<значение1>, <значение2>, ...)` | Добавить запись |
| `select from <имя_таблицы> [where <столбец> = <значение>]` | Выбрать записи |
| `update <имя_таблицы> set <столбец> = <значение> where <столбец> = <значение>` | Обновить запись |
| `delete from <имя_таблицы> where <столбец> = <значение>` | Удалить запись |
| `info <имя_таблицы>` | Информация о таблице |

### Пример использования

```bash
$ database

>>> Введите команду: insert into users values ("Sergei", 28, true)
Запись с ID=1 успешно добавлена в таблицу "users".

>>> Введите команду: select from users where age = 28
+----+--------+-----+-----------+
| ID |  name  | age | is_active |
+----+--------+-----+-----------+
| 1  | Sergei | 28  |    True   |
+----+--------+-----+-----------+

>>> Введите команду: update users set age = 29 where name = "Sergei"
Запись с ID=1 в таблице "users" успешно обновлена.

>>> Введите команду: delete from users where ID = 1
Запись с ID=1 успешно удалена из таблицы "users".

>>> Введите команду: info users
Таблица: users
Столбцы: ID:int, name:str, age:int, is_active:bool
Количество записей: 0
