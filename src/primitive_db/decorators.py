"""Декораторы и замыкания для улучшения кода."""

import time

import prompt


def handle_db_errors(func):
    """Декоратор для централизованной обработки ошибок БД.

    Перехватывает KeyError, ValueError, FileNotFoundError
    и выводит понятные сообщения пользователю.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

    return wrapper


def confirm_action(action_name):
    """Фабрика декораторов для запроса подтверждения действия.

    Args:
        action_name: описание действия для пользователя.

    Returns:
        Декоратор, запрашивающий подтверждение перед выполнением функции.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            answer = prompt.string(
                f'Вы уверены, что хотите выполнить '
                f'"{action_name}"? [y/n]: '
            )
            if answer.lower() != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Декоратор для замера времени выполнения функции.

    Выводит время выполнения в формате:
    Функция <имя_функции> выполнилась за X.XXX секунд.
    """

    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        print(
            f"Функция {func.__name__} "
            f"выполнилась за {end - start:.3f} секунд."
        )
        return result

    return wrapper


def create_cacher():
    """Создаёт функцию кэширования на основе замыкания.

    Returns:
        Функция cache_result(key, value_func).
    """
    cache = {}

    def cache_result(key, value_func):
        """Возвращает результат из кэша или вычисляет его.

        Args:
            key: ключ кэша.
            value_func: функция для получения данных.

        Returns:
            Кэшированный или вычисленный результат.
        """
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    return cache_result


# Глобальный экземпляр кэша для использования в проекте
cacher = create_cacher()
