import timeit
from functools import lru_cache
import matplotlib.pyplot as plt
import sys


# Реалізація Fibonacci через lru_cache
@lru_cache(maxsize=None)
def fibonacci_lru(n):
    """Обчислення n-го числа Фібоначчі з використанням lru_cache."""
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


# Скидаємо кеш між серіями вимірювань, аби був "чистий" старт
def reset_lru_cache():
    fibonacci_lru.cache_clear()


# Реалізація Splay Tree
class SplayNode:
    """Вузол Splay Tree, зберігає пару (key, value)."""
    __slots__ = ('key', 'value', 'left', 'right')

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class SplayTree:
    """
    Базова реалізація Splay Tree.
    У ній зберігається (key, value) -> (n, fibonacci(n)).
    """

    def __init__(self):
        self.root = None

    def _right_rotate(self, x):
        """Праве обертання навколо вузла x."""
        y = x.left
        x.left = y.right
        y.right = x
        return y

    def _left_rotate(self, x):
        """Ліве обертання навколо вузла x."""
        y = x.right
        x.right = y.left
        y.left = x
        return y

    def _splay(self, root, key):
        """
        Головна операція «splay». Підтягує вузол з даним ключем key
        (або останній відомий вузол на шляху до key) у корінь дерева.
        """
        if root is None or root.key == key:
            return root

        # Zig-Zig або Zig-Zag залежно від розташування key.
        # Key в лівому піддереві
        if key < root.key:
            if root.left is None:
                return root
            # Zig-Zig (Left Left)
            if key < root.left.key:
                root.left.left = self._splay(root.left.left, key)
                root = self._right_rotate(root)
            # Zig-Zag (Left Right)
            elif key > root.left.key:
                root.left.right = self._splay(root.left.right, key)
                if root.left.right is not None:
                    root.left = self._left_rotate(root.left)

            return root if root.left is None else self._right_rotate(root)

        # Key в правому піддереві
        else:
            if root.right is None:
                return root
            # Zig-Zig (Right Right)
            if key > root.right.key:
                root.right.right = self._splay(root.right.right, key)
                root = self._left_rotate(root)
            # Zig-Zag (Right Left)
            elif key < root.right.key:
                root.right.left = self._splay(root.right.left, key)
                if root.right.left is not None:
                    root.right = self._right_rotate(root.right)

            return root if root.right is None else self._left_rotate(root)

    def search(self, key):
        """Пошук значення за ключем key. Якщо знайдено – root буде елементом із цим ключем."""
        self.root = self._splay(self.root, key)
        if self.root and self.root.key == key:
            return self.root.value
        return None

    def insert(self, key, value):
        """Вставка нового вузла (key, value). Після вставки робимо splay."""
        if self.root is None:
            self.root = SplayNode(key, value)
            return

        # Спершу виконаємо splay, щоб останнім обробленим був key
        self.root = self._splay(self.root, key)

        # Якщо після splay ключ уже в корені (знайшли існуючий), просто оновимо value.
        if self.root.key == key:
            self.root.value = value
            return

        # Інакше створюємо новий вузол
        new_node = SplayNode(key, value)
        # Розрізаємо дерево за ключем
        if key < self.root.key:
            new_node.right = self.root
            new_node.left = self.root.left
            self.root.left = None
        else:
            new_node.left = self.root
            new_node.right = self.root.right
            self.root.right = None

        self.root = new_node  # новий вузол стає коренем


# Фібоначчі з використанням Splay Tree
def fibonacci_splay(n, tree):
    """
    Обчислення n-го числа Фібоначчі з використанням Splay Tree tree
    як “кешу” обчислених результатів.
    """
    # Перевіряємо, чи є таке n у дереві
    cached_val = tree.search(n)
    if cached_val is not None:
        return cached_val

    # Якщо у дереві немає – обчислюємо
    if n < 2:
        result = n
    else:
        result = fibonacci_splay(n - 1, tree) + fibonacci_splay(n - 2, tree)

    # Зберігаємо отриманий результат у splay-дереві
    tree.insert(n, result)
    return result


def reset_splay_tree():
    """Повністю створює нове дерево (щоб почати обчислення «з нуля»)."""
    return SplayTree()


# Вимірювання часу
def measure_time(func, setup, number=950):
    """
    Повертає середній час (у секундах), витрачений на виклик `func()`,
    вимірюючи через timeit.repeat або timeit.timeit.
    Параметр `number` - скільки повторів робити (більше повторів -> точніший результат).
    """
    t = timeit.timeit(func, setup=setup, number=number)
    return t / number


def main():
    sys.setrecursionlimit(10 ** 7)  # про всяк випадок, щоб уникнути проблем із глибиною рекурсії

    ns = list(range(0, 951, 50))  # 0, 50, 100, 150, ... 950)

    # Кожну функцію викликаємо кілька разів і вимірюємо середній час.
    # Для демонстрації достатньо 100 або 200 повторів, аби не затягувати.
    repeat_count = 200

    results_lru = []
    results_splay = []

    print("n         LRU Cache Time (s)    Splay Tree Time (s)")
    print("----------------------------------------------------")

    for n in ns:
        # ---------- LRU Cache заміри ----------
        # Скидаємо кеш, щоб кожне n починати обчислювати "з нуля"
        reset_lru_cache()

        # Збірка необхідних рядків для timeit
        setup_lru = (
            "from __main__ import fibonacci_lru;"
            f"n={n}"
        )
        code_lru = f"fibonacci_lru({n})"

        t_lru = measure_time(code_lru, setup_lru, number=repeat_count)
        results_lru.append(t_lru)

        # ---------- Splay Tree заміри ----------
        # Нове дерево для кожного n
        setup_splay = (
            "from __main__ import fibonacci_splay, reset_splay_tree;"
            "tree = reset_splay_tree();"
            f"n = {n}"
        )
        code_splay = "fibonacci_splay(n, tree)"

        t_splay = measure_time(code_splay, setup_splay, number=repeat_count)
        results_splay.append(t_splay)

        print(f"{n:<10} {t_lru:<20.8g} {t_splay:<20.8g}")

    # Побудова графіка
    plt.figure(figsize=(8, 5))
    plt.plot(ns, results_lru, 'o-', label="LRU Cache")
    plt.plot(ns, results_splay, 'x-', label="Splay Tree")

    plt.title("Порівняння часу виконання для LRU Cache та Splay Tree")
    plt.xlabel("Число Фібоначчі (n)")
    plt.ylabel("Середній час виконання (секунди)")
    plt.legend()
    plt.grid(True)

    plt.show()


if __name__ == "__main__":
    main()

    # n         LRU Cache Time (s)    Splay Tree Time (s)
    # ----------------------------------------------------
    # 0          6.1499886e-08        4.2699976e-07
    # 50         7.7500008e-08        4.9100025e-07
    # 100        8.3499472e-08        8.0000027e-07
    # 150        9.1500115e-08        1.2755004e-06
    # 200        1.0249962e-07        1.6644999e-06
    # 250        1.1300028e-07        2.1565001e-06
    # 300        1.2999983e-07        2.3400004e-06
    # 350        1.3699988e-07        2.7414999e-06
    # 400        1.7000013e-07        3.0164997e-06
    # 450        1.6250007e-07        3.515e-06
    # 500        1.7549959e-07        4.3490005e-06
    # 550        1.8800027e-07        5.2290002e-06
    # 600        2.5450019e-07        4.5499997e-06
    # 650        2.164999e-07         4.8649998e-06
    # 700        2.3550005e-07        5.4179999e-06
    # 750        2.4400011e-07        6.7645003e-06
    # 800        3.0399999e-07        9.1489998e-06
    # 850        2.7199974e-07        6.4225e-06
    # 900        2.8349983e-07        7.4049999e-06
    # 950        3.055e-07            7.5049995e-06
