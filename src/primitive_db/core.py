"""Основная логика работы с таблицами и данными."""

from primitive_db.constants import VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    handle_db_errors,
    log_time,
)


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создает новую таблицу в метаданных.

    Args:
        metadata: текущий словарь метаданных.
        table_name: имя новой таблицы.
        columns: список столбцов в формате 'имя:тип'.

    Returns:
        Обновленный словарь метаданных.

    Raises:
        ValueError: если таблица уже существует, тип некорректен
                    или столбцы не заданы.
    """
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    if not columns:
        raise ValueError("Необходимо указать хотя бы один столбец.")

    parsed_columns = []
    for col in columns:
        if ":" not in col:
            raise ValueError(
                f'Некорректный формат столбца: "{col}". '
                f'Ожидается "имя:тип".'
            )
        name, col_type = col.split(":", 1)
        if col_type not in VALID_TYPES:
            raise ValueError(
                f'Некорректный тип "{col_type}" для столбца "{name}". '
                f'Допустимые типы: {", ".join(VALID_TYPES)}.'
            )
        parsed_columns.append({"name": name, "type": col_type})

    full_columns = [{"name": "ID", "type": "int"}] + parsed_columns

    metadata[table_name] = {"columns": full_columns}

    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных.

    Args:
        metadata: текущий словарь метаданных.
        table_name: имя удаляемой таблицы.

    Returns:
        Обновленный словарь метаданных.

    Raises:
        KeyError: если таблица не существует.
    """
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')

    del metadata[table_name]

    return metadata


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Добавляет новую запись в таблицу.

    Args:
        metadata: словарь метаданных.
        table_name: имя таблицы.
        values: список значений (без ID), уже преобразованных к типам.

    Returns:
        Список обновленных данных таблицы.

    Raises:
        KeyError: если таблица не существует.
        ValueError: если количество значений некорректно.
    """
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')

    columns = metadata[table_name]["columns"]
    data_columns = columns[1:]

    if len(values) != len(data_columns):
        raise ValueError(
            f'Ожидалось {len(data_columns)} значений, '
            f'получено {len(values)}.'
        )

    from primitive_db.utils import load_table_data
    table_data = load_table_data(table_name)

    if table_data:
        new_id = max(row["ID"] for row in table_data) + 1
    else:
        new_id = 1

    record = {"ID": new_id}
    for col, val in zip(data_columns, values):
        record[col["name"]] = val

    table_data.append(record)

    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Выбирает записи из таблицы.

    Args:
        table_data: список записей таблицы.
        where_clause: словарь условий фильтрации (или None).

    Returns:
        Отфильтрованный список записей.
    """
    if where_clause is None:
        return table_data

    result = []
    for row in table_data:
        match = True
        for key, value in where_clause.items():
            if key not in row or row[key] != value:
                match = False
                break
        if match:
            result.append(row)
    return result


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет записи в таблице.

    Args:
        table_data: список записей таблицы.
        set_clause: словарь полей для обновления.
        where_clause: словарь условий поиска.

    Returns:
        Кортеж (обновленные данные, количество изменений).
    """
    updated_count = 0
    for row in table_data:
        match = True
        for key, value in where_clause.items():
            if key not in row or row[key] != value:
                match = False
                break
        if match:
            for key, value in set_clause.items():
                row[key] = value
            updated_count += 1
    return table_data, updated_count


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    """Удаляет записи из таблицы.

    Args:
        table_data: список записей таблицы.
        where_clause: словарь условий для удаления.

    Returns:
        Кортеж (оставшиеся данные, количество удалений).
    """
    original_count = len(table_data)
    filtered = []
    for row in table_data:
        match = True
        for key, value in where_clause.items():
            if key not in row or row[key] != value:
                match = False
                break
        if not match:
            filtered.append(row)
    deleted_count = original_count - len(filtered)
    return filtered, deleted_count


@handle_db_errors
def get_table_info(metadata, table_name, data_count):
    """Формирует информацию о таблице.

    Args:
        metadata: словарь метаданных.
        table_name: имя таблицы.
        data_count: количество записей.

    Returns:
        Словарь с информацией о таблице.

    Raises:
        KeyError: если таблица не существует.
    """
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')

    columns = metadata[table_name]["columns"]
    columns_str = ", ".join(
        f"{col['name']}:{col['type']}" for col in columns
    )
    return {
        "name": table_name,
        "columns": columns_str,
        "count": data_count,
    }
