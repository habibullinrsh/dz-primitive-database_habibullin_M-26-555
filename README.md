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

<script id="asciicast-2SdGOVbUBcYIzVxI" src="https://asciinema.org/a/2SdGOVbUBcYIzVxI.js" async></script>
