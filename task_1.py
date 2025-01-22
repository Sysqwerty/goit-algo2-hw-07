import random
import time
from collections import OrderedDict


# Функції без кешування
def range_sum_no_cache(array, L, R):
    """
    Повертає суму елементів array[L]...array[R] (включно) без використання кешу.
    """
    return sum(array[L:R + 1])


def update_no_cache(array, index, value):
    """
    Оновлює значення елемента масиву array[index] на value без кешу.
    """
    array[index] = value


# Реалізація LRU-кешу
class LRUCache:
    """
    Клас для зберігання результатів range-сум у форматі:
    cache[(L, R)] = сума від L до R

    Використовуємо OrderedDict для автоматичного відслідковування порядку використання.
    Ключ - це кортеж (L, R).
    Значення - це обчислена сума array[L]...array[R].
    """

    def __init__(self, capacity=1000):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        """
        Отримуємо значення з кешу за ключем (L, R).
        Якщо ключ існує, пересуваємо його в кінець (як найновіше використання).
        Якщо ключа немає, повертаємо None.
        """
        if key not in self.cache:
            return None
        # Пересуваємо в кінець, оскільки ключ використаний
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        """
        Додаємо (або оновлюємо) значення в кеш.
        Якщо розмір кешу перевищує capacity, видаляємо LRU-елемент.
        """
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # видаляємо найстаріший (LRU)

    def invalidate(self, condition_func):
        """
        Видаляє всі елементи кешу, для яких виконується умова condition_func(key).
        Наприклад, якщо condition_func перевіряє, чи (L <= index <= R).
        """
        keys_to_remove = [k for k in self.cache.keys() if condition_func(k)]
        for k in keys_to_remove:
            del self.cache[k]


# Функції з кешуванням
def range_sum_with_cache(array, L, R, lru_cache):
    """
    Повертає суму елементів array[L]...array[R] (включно),
    використовуючи lru_cache, щоб уникнути повторних обчислень.
    """
    # 1. Перевірити, чи є (L, R) у кеші
    cached_value = lru_cache.get((L, R))
    if cached_value is not None:
        # Якщо в кеші є, повертаємо швидко
        return cached_value

    # 2. Якщо в кеші немає, обчислюємо суму й кладемо у кеш
    s = sum(array[L:R + 1])
    lru_cache.put((L, R), s)
    return s


def update_with_cache(array, index, value, lru_cache):
    """
    Оновлює значення у масиві та інвалідовує (видаляє) з кешу
    всі записи, які стали неактуальними.
    """
    array[index] = value

    # Усі кешовані відрізки, які включають index, більше не актуальні
    # Тому видаляємо їх із кешу
    def condition(key):
        L, R = key
        return (L <= index <= R)

    lru_cache.invalidate(condition)


# Приклад тесту продуктивності
def main():
    N = 100_000  # розмір масиву
    Q = 50_000  # кількість запитів
    CAPACITY = 1000  # розмір LRU-кешу

    # Генеруємо випадковий масив із N елементів
    array = [random.randint(1, 1000) for _ in range(N)]

    # Генеруємо випадкові запити
    # Половина з них - 'Range', половина - 'Update' (або як вам потрібно)
    queries = []
    for _ in range(Q):
        query_type = random.choice(["Range", "Update"])
        if query_type == "Range":
            L = random.randint(0, N - 1)
            R = random.randint(L, N - 1)
            queries.append(("Range", L, R))
        else:  # Update
            index = random.randint(0, N - 1)
            value = random.randint(1, 1000)
            queries.append(("Update", index, value))

    # Виконання запитів без кешування
    start_time_no_cache = time.perf_counter()

    array_no_cache = array[:]  # копія вихідного масиву
    for q in queries:
        if q[0] == "Range":
            _, L, R = q
            _ = range_sum_no_cache(array_no_cache, L, R)
        else:
            _, idx, val = q
            update_no_cache(array_no_cache, idx, val)

    end_time_no_cache = time.perf_counter()
    total_time_no_cache = end_time_no_cache - start_time_no_cache

    # Виконання запитів з LRU-кешем
    start_time_cache = time.perf_counter()

    array_with_cache = array[:]  # копія вихідного масиву
    lru_cache = LRUCache(capacity=CAPACITY)

    for q in queries:
        if q[0] == "Range":
            _, L, R = q
            _ = range_sum_with_cache(array_with_cache, L, R, lru_cache)
        else:
            _, idx, val = q
            update_with_cache(array_with_cache, idx, val, lru_cache)

    end_time_cache = time.perf_counter()
    total_time_cache = end_time_cache - start_time_cache

    # Вивід результатів
    print(f"Час виконання без кешування: {total_time_no_cache:.3f} cекунд")
    print(f"Час виконання з LRU-кешем: {total_time_cache:.3f} cекунд")


if __name__ == "__main__":
    main()

    # Час виконання без кешування: 9.730 cекунд
    # Час виконання з LRU-кешем: 10.471 cекунд
