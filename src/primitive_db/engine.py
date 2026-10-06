"""Модуль для запуска, игрового цикла и парсинга команд."""

import shlex

import prompt

from primitive_db.constants import META_FILE
from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata


def print_help():
    """Prints the help message for the current mode."""
    
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


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
                try:
                    metadata = create_table(metadata, table_name, columns)
                    save_metadata(META_FILE, metadata)
                    col_names = ", ".join(
                        f"{col['name']}:{col['type']}"
                        for col in metadata[table_name]["columns"]
                    )
                    print(
                        f'Таблица "{table_name}" успешно создана '
                        f'со столбцами: {col_names}'
                    )
                except ValueError as e:
                    print(f"Ошибка: {e}")
            case "drop_table":
                if len(args) != 2:
                    print("Некорректное значение. Попробуйте снова.")
                    continue
                table_name = args[1]
                try:
                    metadata = drop_table(metadata, table_name)
                    save_metadata(META_FILE, metadata)
                    print(f'Таблица "{table_name}" успешно удалена.')
                except KeyError as e:
                    print(f"Ошибка: {e}")
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")
