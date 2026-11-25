# Задание 1. Ленивая обработка выгрузки продаж

# Напишите набор функций-этапов для обработки CSV-выгрузки продаж. Файл может быть больше оперативной памяти, поэтому все этапы, кроме итоговых агрузок, должны быть генераторами. Модуль csv использовать можно, но и split(',') достаточно.
# Формат файла: первая непустая и не-комментарная строка это заголовок date,category,product,qty,price. Строки, начинающиеся с #, и пустые строки пропускаются. Файл упорядочен по дате.
# Функции:
# read_sales(path, errors=None): генератор словарей вида {'date': '2026-10-01', 'category': 'food', 'product': 'tea', 'qty': 3, 'price': 120.5}. Битые строки (не то число полей, нечисловые qty или price) пропускаются. Если передан список errors, в него добавляется пара (номер строки в файле, текст строки);
# daily_revenue(rows): генератор пар (дата, выручка за день), выручка округлена до 2 знаков. Используйте то, что файл упорядочен по дате;
# running_revenue(daily): генератор пар (дата, выручка нарастающим итогом);
# revenue_by_category(rows): словарь {категория: выручка};
# best_days(daily, n=3): список из n самых прибыльных дней, по убыванию выручки. Подумайте, как сделать это без сортировки всех дней (подсказка: модуль heapq).
# Проверка на большом файле. Сгенерируйте выгрузку за год (около 1 млн строк, 30 МБ) скриптом ниже и измерьте через tracemalloc пик памяти для best_days(daily_revenue(read_sales('sales_big.csv'))). Пик должен быть меньше 1 МБ. Результат замера запишите в комментарий.
# В комментарии ответьте: почему daily_revenue дал бы неправильный результат на неупорядоченном файле, и как бы вы решили задачу в этом случае (какой ценой по памяти)?

from datetime import date, timedelta
import heapq
import random
import tracemalloc
import types

SAMPLE = """# выгрузка продаж
date,category,product,qty,price

2026-10-01,books,Dune,2,500
2026-10-01,food,tea,3,120.5
2026-10-02,books,Solaris,1,450
# комментарий посреди файла
2026-10-02,food,coffee,много,300
2026-10-02,toys,ball,4,250
2026-10-03,food,tea,10,120.5
2026-10-03,books,Dune
"""


def read_sales(path, errors=None):
    with open(path, "r", encoding="utf-8") as f:
        header_found = False

        for line_no, raw_line in enumerate(f, start=1):
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if not header_found:
                header_found = True
                continue

            parts = line.split(",")
            if len(parts) != 5:
                if errors is not None:
                    errors.append((line_no, raw_line.rstrip("\r\n")))
                continue

            date_str, category, product, qty_str, price_str = parts

            try:
                qty = int(qty_str)
                price = float(price_str)
            except ValueError:
                if errors is not None:
                    errors.append((line_no, raw_line.rstrip("\r\n")))
                continue

            yield {
                "date": date_str,
                "category": category,
                "product": product,
                "qty": qty,
                "price": price,
            }


def daily_revenue(rows):
    current_date = None
    current_total = 0.0

    for r in rows:
        row_date = r["date"]
        revenue = r["qty"] * r["price"]

        if current_date is None:
            current_date = row_date
            current_total = revenue
        elif row_date == current_date:
            current_total += revenue
        else:
            yield (current_date, round(current_total, 2))
            current_date = row_date
            current_total = revenue

    if current_date is not None:
        yield (current_date, round(current_total, 2))


def running_revenue(daily):
    cumulative = 0.0
    for current_date, revenue in daily:
        cumulative += revenue
        yield (current_date, round(cumulative, 2))


def revenue_by_category(rows):
    categories = {}
    for r in rows:
        cat = r["category"]
        rev = r["qty"] * r["price"]
        categories[cat] = categories.get(cat, 0.0) + rev

    return {cat: round(val, 2) for cat, val in categories.items()}


def best_days(daily, n=3):
    return heapq.nlargest(n, daily, key=lambda item: item[1])


def make_big(path='sales_big.csv', days=365, rows_per_day=3000):
    random.seed(0)
    cats = {'books': ['Dune', 'Solaris'], 'food': ['tea', 'coffee'], 'toys': ['ball', 'lego']}
    start = date(2025, 1, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('date,category,product,qty,price\n')
        for d in range(days):
            day = (start + timedelta(days=d)).isoformat()
            for _ in range(rows_per_day):
                c = random.choice(list(cats))
                qty = random.randint(1, 5) if random.random() > 0.001 else 'oops'
                f.write(f'{day},{c},{random.choice(cats[c])},{qty},{random.randint(50, 900)}\n')


if __name__ == '__main__':
    with open('sales_sample.csv', 'w', encoding='utf-8') as f:
        f.write(SAMPLE)

    errors = []
    rows = list(read_sales('sales_sample.csv', errors))
    assert len(rows) == 5
    assert rows[1] == {'date': '2026-10-01', 'category': 'food', 'product': 'tea', 'qty': 3, 'price': 120.5}
    assert [no for no, _ in errors] == [8, 11]

    daily = list(daily_revenue(read_sales('sales_sample.csv')))
    assert daily == [('2026-10-01', 1361.5), ('2026-10-02', 1450.0), ('2026-10-03', 1205.0)]
    assert list(running_revenue(iter(daily))) == [
        ('2026-10-01', 1361.5), ('2026-10-02', 2811.5), ('2026-10-03', 4016.5)]
    assert revenue_by_category(read_sales('sales_sample.csv')) == {
        'books': 1450.0, 'food': 1566.5, 'toys': 1000.0}
    assert best_days(daily_revenue(read_sales('sales_sample.csv')), 2) == [
        ('2026-10-02', 1450.0), ('2026-10-01', 1361.5)]
    assert isinstance(read_sales('sales_sample.csv'), types.GeneratorType)
    assert isinstance(daily_revenue([]), types.GeneratorType)

    make_big("sales_big.csv")
    print("Файл sales_big.csv успешно создан.")

    tracemalloc.start()
    top_3 = best_days(daily_revenue(read_sales("sales_big.csv")), 3)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Пик памяти: {peak / 1024 / 1024:.4f} МБ")
    print("Топ-3 прибыльных дня:", top_3)

# Комментарий:

# Почему daily_revenue дал бы неправильный результат на неупорядоченном файле?
# Функция daily_revenue предполагает, что все записи одного дня идут строго подряд.
# Как только встречается новая дата, функция "закрывает" предыдущий день и отдает
# сумму через yield. Если файл не отсортирован, одна и та же дата встретится
# в разных частях файла несколько раз и выдаст несколько неполных сумм вместо одной.

# Как решить задачу для неупорядоченного файла и какой ценой по памяти?
# Решение: читать файл построчно и складывать выручку в обычный словарь:
# totals[date] = totals.get(date, 0.0) + rev. После прочтения всего файла
# сделать yield для каждой пары из словаря.
# Цена по памяти: O(n), где n — количество уникальных дат в файле.
# Для файла за год это всего 365 ключей в словаре (несколько килобайт памяти),
# поэтому решение по-прежнему легко уложится в лимит до 1 МБ.