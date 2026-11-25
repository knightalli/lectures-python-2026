from collections import deque
from itertools import zip_longest


def read_orders(path):
    """Лениво читает заказы из файла: на каждой строке user,amount."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield line.split(",")


def totals_by_user(orders):
    """Сумма заказов по каждому пользователю."""
    result = {}
    for user, amount in orders:
        result[user] = result.get(user, 0.0) + float(amount)
    return result


def has_large_orders(orders, threshold=1000):
    """Есть ли хотя бы один заказ дороже threshold."""
    return any(float(amount) > threshold for _, amount in orders)


def vip_over_limit(totals, vip_users, vip_limits):
    """VIP-клиенты, превысившие свой лимит.

    Для клиентов без лимита лимит считается бесконечным.
    """
    result = []
    for u, limit in zip_longest(vip_users, vip_limits, fillvalue=float("inf")):
        if limit is None:
            limit = float("inf")
        if totals.get(u, 0.0) > limit:
            result.append(u)
    return result


def last_orders(path, n=5):
    """Последние n непустых строк файла заказов через deque без чтения всего файла в память."""
    with open(path, "r", encoding="utf-8") as f:
        tail = deque((line.strip() for line in f if line.strip()), maxlen=n)
    return list(tail)


def build_report(path, vip_users, vip_limits):
    """Формирует отчет за один проход по файлу, не перегружая память."""
    orders = list(read_orders(path))   
    count = len(orders)
    totals = totals_by_user(orders)
    return {
        'orders': count,
        'totals': totals,
        'has_large': has_large_orders(orders),
        'vip_over_limit': vip_over_limit(totals, vip_users, vip_limits),
        'last': last_orders(path, 3),
    }


if __name__ == "__main__":
    with open('orders.txt', 'w', encoding='utf-8') as f:
        f.write('anna,100\nbob,50\n\nanna,700\nkate,300\nbob,30\n')
    report = build_report('orders.txt', ['anna', 'bob', 'kate'], [500, 10])
    print(report)
    