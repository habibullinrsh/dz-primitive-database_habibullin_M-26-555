"""Модуль для запуска, игрового цикла и парсинга команд."""

import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import META_FILE
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    get_table_info,
    insert,
    select,
    update,
)
from primitive_db.decorators import cacher
from primitive_db.parser import (
    parse_set_clause,
    parse_values,
    parse_where_clause,
)
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Выводит справочную информацию."""
    print("\n***Операции с данными***\n")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> "
        "<столбец1:тип> <столбец2:тип> .. - создать таблицу"
    )
    print(
        "<command> insert into <имя_таблицы> "
        "values (<значение1>, <значение2>, ...) - создать запись"
    )
    print(
        "<command> select from <имя_таблицы> "
        "[where <столбец> = <значение>] - прочитать записи"
    )
    print(
        "<command> update <имя_таблицы> set "
        "<столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> "
        "- обновить запись"
    )
    print(
        "<command> delete from <имя_таблицы> "
        "where <столбец> = <значение> - удалить запись"
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def _print_table(table_data, columns):
    """Выводит данные таблицы в красивом формате.

    Args:
        table_data: список записей.
        columns: список столбцов из метаданных.
    """
    table = PrettyTable()
    table.field_names = [col["name"] for col in columns]
    for row in table_data:
        table.add_row([row[col["name"]] for col in columns])
    print(table)


def run():
    """Основной цикл программы."""
    print("\n***База данных***\n")
    print_help()

    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(">>>Введите команду: ")

        if not user_input.strip():
            continue

        args = shlex.split(user_input)
        command = args[0]

        match command:
            case "exit":
                break
            case "help":
                print_help()
            case "list_tables":
                if not metadata:
                    print("Таблицы отсутствуют.")
                else:
                    for table_name in metadata:
                        print(f"- {table_name}")
            case "create_table":
                if len(args) < 3:
                    print("Некорректное значение. Попробуйте снова.")
                    continue
                table_name = args[1]
                columns = args[2:]
                result = create_table(metadata, table_name, columns)
                if result is not None:
                    metadata = result
                    save_metadata(META_FILE, metadata)
                    col_names = ", ".join(
                        f"{col['name']}:{col['type']}"
                        for col in metadata[table_name]["columns"]
                    )
                    print(
                        f'Таблица "{table_name}" успешно создана '
                        f'со столбцами: {col_names}'
                    )
            case "drop_table":
                if len(args) != 2:
                    print("Некорректное значение. Попробуйте снова.")
                    continue
                table_name = args[1]
                result = drop_table(metadata, table_name)
                if result is not None:
                    metadata = result
                    save_metadata(META_FILE, metadata)
                    print(f'Таблица "{table_name}" успешно удалена.')
            case "insert":
                if (
                    len(args) < 4
                    or args[1] != "into"
                    or args[3] != "values"
                ):
                    print("Некорректное значение. Попробуйте снова.")
                    continue
                table_name = args[2]
                if table_name not in metadata:
                    print(
                        f'Ошибка: Таблица "{table_name}" '
                        f'не существует.'
                    )
                    continue
                values_part = " ".join(args[4:])
                values_part = values_part.strip("() ")
                raw_values = [v.strip() for v in values_part.split(",")]
                values = parse_values(raw_values)
                result = insert(metadata, table_name, values)
                if result is not None:
                    save_table_data(table_name, result)
                    new_id = result[-1]["ID"]
                    print(
                        f'Запись с ID={new_id} успешно добавлена '
                        f'в таблицу "{table_name}".'
                    )
            case "select":
                if len(args) < 3 or args[1] != "from":
                    print("Некорректное значение. Попробуйте снова.")
                    continue
                table_name = args[2]
                if table_name not in metadata:
                    print(
                        f'Ошибка: Таблица "{table_name}" '
                        f'не существует.'
                    )
                    continue
                where_clause = None
                if len(args) > 3 and args[3] == "where":
                    try:
                        where_clause = parse_where_clause(args[4:])
                    except ValueError as e:
                        print(f"Ошибка: {e}")
                        continue
                table_data = load_table_data(table_name)

                # Кэширование результата select
                cache_key = (table_name, str(where_clause))
                result = cacher(
                    cache_key,
                    lambda td=table_data, wc=where_clause: select(td, wc),
                )

                columns = metadata[table_name]["columns"]
                if result is None or not result:
                    print("Записи не найдены.")
                else:
                    _print_table(result, columns)
            case "update":
                if (
                    len(args) < 6
                    or args[2] != "set"
                    or "where" not in args
                ):
                    print("Некорректное значение. Попробуйте снова.")
                    continue
                table_name = args[1]
                if table_name not in metadata:
                    print(
                        f'Ошибка: Таблица "{table_name}" '
                        f'не существует.'
                    )
                    continue
                where_idx = args.index("where")
                set_args = args[3:where_idx]
                where_args = args[where_idx + 1:]
                try:
                    set_clause = parse_set_clause(set_args)
                    where_clause = parse_where_clause(where_args)
                except ValueError as e:
                    print(f"Ошибка: {e}")
                    continue
                table_data = load_table_data(table_name)
                result = update(table_data, set_clause, where_clause)
                if result is not None:
                    table_data, count = result
                    save_table_data(table_name, table_data)
                    if count > 0:
                        print(
                            f'Запись в таблице "{table_name}" '
                            f'успешно обновлена.'
                        )
                    else:
                        print("Записи для обновления не найдены.")
            case "delete":
                if (
                    len(args) < 5
                    or args[1] != "from"
                    or args[3] != "where"
                ):
                    print("Некорректное значение. Попробуйте снова.")
                    continue
                table_name = args[2]
                if table_name not in metadata:
                    print(
                        f'Ошибка: Таблица "{table_name}" '
                        f'не существует.'
                    )
                    continue
                try:
                    where_clause = parse_where_clause(args[4:])
                except ValueError as e:
                    print(f"Ошибка: {e}")
                    continue
                table_data = load_table_data(table_name)
                result = delete(table_data, where_clause)
                if result is not None:
                    table_data, count = result
                    save_table_data(table_name, table_data)
                    if count > 0:
                        print(
                            f'Запись успешно удалена '
                            f'из таблицы "{table_name}".'
                        )
                    else:
                        print("Записи для удаления не найдены.")
            case "info":
                if len(args) != 2:
                    print("Некорректное значение. Попробуйте снова.")
                    continue
                table_name = args[1]
                table_data = load_table_data(table_name)
                result = get_table_info(
                    metadata, table_name, len(table_data)
                )
                if result is not None:
                    print(f'Таблица: {result["name"]}')
                    print(f'Столбцы: {result["columns"]}')
                    print(f'Количество записей: {result["count"]}')
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")
