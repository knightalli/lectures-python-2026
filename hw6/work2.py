#Задание 2. Свой диапазон дат

#Напишите класс DateRange(start, stop, step=1), аналог range для дат: от start включительно до stop не включительно, step в днях. Это повторение протокола итерации (лекция 6) и протокола контейнера (лекция 7).
# Требования:
# по объекту можно пройти сколько угодно раз, и вложенные циклы по одному объекту работают правильно;
# len(r), r[i] с отрицательными индексами и IndexError за пределами;
# d in r работает за O(1), без перебора дат (проверка ниже на диапазоне в 3.6 млн дней должна выполняться мгновенно);
# reversed(r) работает без создания списка всех дат;
# step <= 0 вызывает ValueError;
# __repr__ и __eq__.
# В комментарии объясните: чем ваш класс отличается от варианта, где __iter__ возвращает self, и какой баг был бы во втором варианте.

from datetime import timedelta


class DateRange:

    def __init__(self, start, stop, step=1):
        if step <= 0:
            raise ValueError("step должен быть больше 0")
        self.start = start
        self.stop = stop
        self.step = step

    def __len__(self):
        total_days = (self.stop - self.start).days
        if total_days <= 0:
            return 0
        return (total_days + self.step - 1) // self.step

    def __iter__(self):
        curr = self.start
        while curr < self.stop:
            yield curr
            curr += timedelta(days=self.step)

    def __getitem__(self, index):
        if index < 0:
            index += len(self)

        if index < 0 or index >= len(self):
            raise IndexError()

        return self.start + timedelta(days=index * self.step)

    def __contains__(self, item):
        if not (self.start <= item < self.stop):
            return False
        return (item - self.start).days % self.step == 0

    def __reversed__(self):
        for i in range(len(self) - 1, -1, -1):
            yield self[i]

    def __repr__(self):
        return f"DateRange({self.start!r}, {self.stop!r}, {self.step})"

    def __eq__(self, other):
        return (self.start, self.stop, self.step) == (
            other.start,
            other.stop,
            other.step,
        )


if __name__ == '__main__':
    from datetime import date
    r = DateRange(date(2026, 10, 1), date(2026, 10, 11), 3)
    assert list(r) == [date(2026, 10, 1), date(2026, 10, 4), date(2026, 10, 7), date(2026, 10, 10)]
    assert list(r) == list(r)
    assert sum(1 for a in r for b in r) == 16
    assert len(r) == 4
    assert len(DateRange(date(2026, 1, 1), date(2026, 1, 1))) == 0
    assert len(DateRange(date(2026, 1, 5), date(2026, 1, 1))) == 0
    assert r[0] == date(2026, 10, 1) and r[-1] == date(2026, 10, 10)
    try:
        r[4]
        assert False, 'ожидали IndexError'
    except IndexError:
        pass
    assert date(2026, 10, 7) in r
    assert date(2026, 10, 8) not in r and date(2026, 10, 13) not in r
    assert list(reversed(r))[0] == date(2026, 10, 10)
    assert repr(r) == 'DateRange(datetime.date(2026, 10, 1), datetime.date(2026, 10, 11), 3)'
    assert DateRange(date(2026, 1, 1), date(2026, 1, 3)) == DateRange(date(2026, 1, 1), date(2026, 1, 3))
    big = DateRange(date(1, 1, 1), date(9999, 12, 31))
    assert date(2026, 10, 17) in big and len(big) == 3652058

# Комментарий:
# В нашем классе __iter__ использует yield, поэтому при каждом вызове
# создается новый независимый генератор. Это позволяет обходить объект сколько угодно раз.
#
# Если бы __iter__ возвращал self, объект сам являлся бы итератором и хранил текущую позицию:
# 1. Повторный вызов list(r) вернул бы пустой список, так как итератор уже исчерпан.
# 2. Во вложенных циклах (for a in r: for b in r:) внутренний цикл исчерпал бы
# итератор на первом же шаге внешнего, и цикл завершился бы досрочно.
