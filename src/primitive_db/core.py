"""Основная логика работы с таблицами и данными."""

from primitive_db.constants import VALID_TYPES


def create_table(metadata, table_name, columns):
    """Создает новую таблицу в метаданных.

    Args:
        metadata: текущий словарь метаданных.
        table_name: имя новой таблицы.
        columns: список столбцов в формате 'имя:тип'.

    Returns:
        Обновленный словарь метаданных.

    Raises:
        ValueError: если таблица уже существует, тип некорректен или столбцы не заданы.
    """
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    if not columns:
        raise ValueError("Необходимо указать хотя бы один столбец.")

    # Проверяем корректность типов данных
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

    # Автоматически добавляем столбец ID:int в начало списка
    full_columns = [{"name": "ID", "type": "int"}] + parsed_columns

    metadata[table_name] = {"columns": full_columns}

    return metadata


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
