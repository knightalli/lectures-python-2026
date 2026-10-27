# Задание 4. Кэширование через замыкание

# В файле `hw4/memoize.py` напишите функцию `memoize(func)`, которая возвращает новую функцию с кэшем результатов.
# Используйте замыкание: кэш (словарь) живет в объемлющей функции, а не в глобальной переменной.
# Требования:
# - ключ кэша строится из позиционных и именованных аргументов, `f(1, b=2)` и `f(1, b=3)` кэшируются отдельно;
# - если аргументы нехешируемые (например, список), функция вызывается без кэша и не падает;
# - у возвращаемой функции есть атрибуты `hits` и `misses` (число попаданий и промахов кэша)
#   и метод `cache_clear()`, который очищает кэш и обнуляет счетчики (вспомните `__dict__` у функций);
# - у возвращаемой функции сохраняются `__name__` и `__doc__` исходной.
# **Эксперимент с рекурсией.** Есть рекурсивная функция
# Сравните два варианта и для каждого выведите `misses` после вызова с `n = 30` и время работы
# Один из вариантов ускоряет вычисление в тысячи раз, другой почти не помогает. В комментарии объясните почему,
# используя правило LEGB: какое имя ищет рекурсивный вызов `fib(n - 1)` внутри функции и в какой момент.


import time


def memoize(func):
    cache = {}

    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))

        try:
            hash(key)
        except TypeError:
            return func(*args, **kwargs)

        if key in cache:
            wrapper.hits += 1
            return cache[key]
        else:
            wrapper.misses += 1
            result = func(*args, **kwargs)
            cache[key] = result
            return result

    def cache_clear():
        cache.clear()
        wrapper.hits = 0
        wrapper.misses = 0

    wrapper.hits = 0
    wrapper.misses = 0
    wrapper.cache_clear = cache_clear

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__

    return wrapper


if __name__ == '__main__':
    calls = []

    def slow_square(x, power=2):
        '''Возводит в степень.'''
        calls.append(x)
        return x ** power

    sq = memoize(slow_square)
    assert sq(3) == 9 and sq(3) == 9 and sq(3, power=3) == 27
    assert calls == [3, 3]
    assert (sq.hits, sq.misses) == (1, 2)
    assert sq.__name__ == 'slow_square' and sq.__doc__ == 'Возводит в степень.'
    total = memoize(sum)
    assert total([1, 2, 3]) == 6 and total([1, 2, 3]) == 6   # нехешируемый аргумент: вызов без кэша
    assert (total.hits, total.misses) == (0, 0)
    sq.cache_clear()
    assert (sq.hits, sq.misses) == (0, 0)
    sq(3)
    assert calls[-1] == 3

    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    fast_fib = memoize(fib)

    start_time = time.perf_counter()
    res_a = fast_fib(30)
    time_a = time.perf_counter() - start_time
    print(f"Вариант A (fast_fib): misses = {fast_fib.misses}, время = {time_a:.4f} сек")

    fib = memoize(fib)

    start_time = time.perf_counter()
    res_b = fib(30)
    time_b = time.perf_counter() - start_time
    print(f"Вариант B (fib)): misses = {fib.misses}, время = {time_b:.4f} сек")


# Комментарий:

# Когда внутри функции срабатывает рекурсия `fib(n - 1)`, python нужно понять, что такое `fib`. 
# Внутри самой функции (L - Local) и снаружи в замыкании (E - Enclosing) такого имени нет. 
# Поэтому он ищет его в глобальной области (G - Global) прямо в момент выполнения вызова.
# 
# 1. В Варианте A мы сохранили умную обертку под новым именем `fast_fib`. 
# А глобальное имя `fib` так и осталось указывать на старую кэша. 
# Поэтому наш кэш сработал только один раз, когда мы вызвали fast_fib. 
# А все рекурсивные вызовов пошли по старому имени `fib` мимо кэша. 
# Поэтому мы и видим всего 1 промах (misses = 1).
# 
# 2. В Варианте B мы написали `fib = memoize(fib)`, то есть прямо перезаписали само 
# глобальное имя `fib`.
# Когда рекурсия внутри вызывает `fib(n - 1)`, python находит в глобальной области (G) 
# уже нашу обертку. Абсолютно каждый шаг проходит через кэш, считаются только 
# уникальные числа от 0 до 30 (отсюда misses = 31), и функция выдает ответ мгновенно.
