"""Парсеры для разбора сложных команд (where, set, values)."""


def _convert_value(value_str):
    """Преобразует строковое значение в нужный тип.

    Args:
        value_str: строковое значение (возможно в кавычках).

    Returns:
        Значение нужного типа (int, bool или str).
    """
    # Убираем кавычки, если они есть
    if (
        (value_str.startswith('"') and value_str.endswith('"'))
        or (value_str.startswith("'") and value_str.endswith("'"))
    ):
        return value_str[1:-1]

    if value_str.lower() == "true":
        return True
    if value_str.lower() == "false":
        return False

    try:
        return int(value_str)
    except ValueError:
        return value_str


def parse_where_clause(args):
    """Разбирает условие where в словарь.

    Ожидает формат: ['column', '=', 'value']

    Args:
        args: список аргументов после 'where'.

    Returns:
        Словарь вида {'column': value}.

    Raises:
        ValueError: если формат некорректен.
    """
    if len(args) != 3 or args[1] != "=":
        raise ValueError(
            'Некорректный формат условия. '
            'Ожидается "столбец = значение".'
        )
    column = args[0]
    value = _convert_value(args[2])
    return {column: value}


def parse_set_clause(args):
    """Разбирает условие set в словарь.

    Ожидает формат: ['column', '=', 'value']

    Args:
        args: список аргументов после 'set'.

    Returns:
        Словарь вида {'column': value}.

    Raises:
        ValueError: если формат некорректен.
    """
    if len(args) != 3 or args[1] != "=":
        raise ValueError(
            'Некорректный формат set. '
            'Ожидается "столбец = значение".'
        )
    column = args[0]
    value = _convert_value(args[2])
    return {column: value}


def parse_values(args):
    """Разбирает список значений из скобок.

    Ожидает формат: ['value1', 'value2', ...]

    Args:
        args: список значений (уже без скобок, разделенных shlex).

    Returns:
        Список значений нужных типов.
    """
    return [_convert_value(val) for val in args]
