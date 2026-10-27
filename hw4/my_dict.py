# Задание 1. Своя хеш-таблица

# В файле `hw4/my_dict.py` реализуйте класс `MyDict`: упрощенный словарь на основе хеш-таблицы с цепочками.
# Внутри класса нельзя использовать `dict` и `set`, только списки и кортежи.
# Требования:
# - корзины хранятся в списке списков, номер корзины: `hash(key) % len(self._buckets)`;
# - при коллизии пары `(key, value)` лежат в одной корзине, нужный ключ ищется через `==`;
# - операции: `d[key] = value`, `d[key]`, `del d[key]`, `key in d`, `len(d)`, `d.get(key, default=None)`;
# - отсутствующий ключ в `d[key]` и `del d[key]` вызывает `KeyError`;
# - когда число элементов становится больше 2/3 от числа корзин, число корзин увеличивается в 2 раза и все пары
#   раскладываются заново;
# - метод `stats()` возвращает кортеж `(число корзин, число элементов, длина самой длинной корзины)`;
# - `__repr__` выводит содержимое в виде `MyDict({'a': 1, 'b': 2})`.
# Ответьте в комментарии в конце файла (2-3 предложения на вопрос):
# 1. Почему при увеличении таблицы пары нельзя просто скопировать в корзины с теми же номерами?
# 2. Что показывает `stats()` для 1000 строковых ключей и что он покажет, если ключами будут объекты,
#    у которых `__hash__` всегда возвращает 42? Проверьте экспериментом, замерьте время вставки 1000 таких ключей.

import time


class MyDict:
    def __init__(self, size=8):
        self._buckets = [[] for _ in range(size)]
        self._len = 0  # Счетчик всех элементов

    def __setitem__(self, key, value):
        hash_idx = hash(key) % len(self._buckets)

        for entry in self._buckets[hash_idx]:
            if entry[0] == key:
                entry[1] = value
                return

        self._buckets[hash_idx].append([key, value])
        self._len += 1

        if self._len > len(self._buckets) * 2 / 3:
            self._resize()

    def __getitem__(self, key):
        hash_idx = hash(key) % len(self._buckets)
        for entry in self._buckets[hash_idx]:
            if entry[0] == key:
                return entry[1]
        raise KeyError(key)

    def __delitem__(self, key):
        hash_idx = hash(key) % len(self._buckets)
        for i, entry in enumerate(self._buckets[hash_idx]):
            if entry[0] == key:
                del self._buckets[hash_idx][i]
                self._len -= 1
                return
        raise KeyError(key)

    def __contains__(self, key):
        hash_idx = hash(key) % len(self._buckets)
        for entry in self._buckets[hash_idx]:
            if entry[0] == key:
                return True
        return False

    def __len__(self):
        return self._len

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def _resize(self):
        new_size = len(self._buckets) * 2
        new_buckets = [[] for _ in range(new_size)]

        for bucket in self._buckets:
            for key, value in bucket:
                new_idx = hash(key) % new_size
                new_buckets[new_idx].append([key, value])

        self._buckets = new_buckets

    def stats(self):
        lengths = [len(bucket) for bucket in self._buckets]
        max_bucket_len = max(lengths)
        return len(self._buckets), self._len, max_bucket_len

    def __repr__(self):
        pairs = []
        for bucket in self._buckets:
            for key, value in bucket:
                pairs.append(f"{repr(key)}: {repr(value)}")
        return f"MyDict({{{', '.join(pairs)}}})"


if __name__ == '__main__':
    d = MyDict()
    for i in range(1000):
        d[f'key{i}'] = i
    assert len(d) == 1000
    assert d['key42'] == 42
    assert 'key7' in d and 'nope' not in d
    d['key42'] = -1
    assert d['key42'] == -1 and len(d) == 1000
    del d['key42']
    assert 'key42' not in d and len(d) == 999
    assert d.get('nope') is None and d.get('nope', 0) == 0
    for bad in (lambda: d['nope'], lambda: d.__delitem__('nope')):
        try:
            bad()
            assert False, 'ожидали KeyError'
        except KeyError:
            pass
    buckets, size, longest = d.stats()
    assert size == 999 and size <= buckets * 2 / 3
    print(d.stats())

    class BadKey:
        def __init__(self, v):
            self.v = v

        def __hash__(self):
            return 42

        def __eq__(self, other):
            return self.v == other.v

    d_normal = MyDict()
    start = time.perf_counter()
    for i in range(1000):
        d_normal[f"test{i}"] = i
    print(f"Нормальные ключи (1000 шт): {time.perf_counter() - start:.4f} сек. Stats: {d_normal.stats()}")

    d_bad = MyDict()
    start = time.perf_counter()
    for i in range(1000):
        d_bad[BadKey(i)] = i
    print(f"Плохие ключи (1000 шт): {time.perf_counter() - start:.4f} сек. Stats: {d_bad.stats()}")

# Комментарий:

# 1. Почему при увеличении таблицы пары нельзя просто скопировать в корзины с теми же номерами?
# Номер корзины считается по формуле: hash % количество_корзин. 
# Если корзин было 8, а стало 16, то остаток от деления для старого хэша изменится. 
# Ключ, который раньше лежал в корзине №5, теперь должен лежать, например, в корзине №13. 
# Если мы оставим его в 5-й, python при поиске посмотрит в 13-ю, ничего там не найдет и выдаст ошибку.
# 
# 2. Что показывает stats() для 1000 строковых ключей и для плохих ключей?
# Для обычных строковых ключей хэши разные. Элементы равномерно ложатся по всем корзинам. 
# Stats показывает, что у нас 2048 корзин, и даже в самой заполненной лежит всего 4 элемента. Скорость записи мгновенная.
# 
# А когда __hash__ всегда равен 42, все 1000 элементов пытаются залезть в одну и ту же корзину
# Stats показывает (2048, 1000, 1000). Наш словарь превратился в обычный длинный список. 
# Скорость падает в сотни раз, потому что python приходится перебирать всю эту тысячу элементов вручную при каждой операции.