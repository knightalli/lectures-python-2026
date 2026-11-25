import importlib
import sys
import inspect

test_file = "test_orders_temp.txt"


def create_test_file():
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("anna,100\nbob,50\n\nanna,700\nkate,300\nbob,30\n")


# 1. Проверка read_orders: чтение из генератора не должно падать из-за закрытого файла
def test_read_orders(mod):
    orders_gen = mod.read_orders(test_file)
    first = next(orders_gen)
    assert first == ["anna", "100"]


# 2. Проверка totals_by_user: корректная сумма при непоследовательных записях одного пользователя
def test_totals_by_user(mod):
    data = [["anna", "100"], ["bob", "50"], ["anna", "700"]]
    res = mod.totals_by_user(data)
    assert res["anna"] == 800.0


# 3. Проверка has_large_orders: не должен возвращать True при отсутствии заказов выше порога
def test_has_large_orders(mod):
    data = [["anna", "100"], ["bob", "50"]]
    assert mod.has_large_orders(data, threshold=1000) is False


# 4. Проверка vip_over_limit: обработка отсутствующего лимита (None) без падения с TypeError
def test_vip_over_limit(mod):
    totals = {"anna": 100.0, "kate": 300.0}
    users = ["anna", "kate"]
    limits = [50, None]
    res = mod.vip_over_limit(totals, users, limits)
    assert res == ["anna"]


# 5. Проверка last_orders: использование deque вместо f.readlines()
def test_last_orders_memory(mod):
    src = inspect.getsource(mod.last_orders)
    assert "deque" in src and "readlines" not in src


# 6. Проверка build_report: totals не должен быть пустым из-за исчерпания генератора
def test_build_report_totals(mod):
    rep = mod.build_report(test_file, ["anna", "bob", "kate"], [500, 10])
    assert rep["orders"] == 5
    assert rep["totals"] == {"anna": 800.0, "bob": 80.0, "kate": 300.0}
    assert rep["vip_over_limit"] == ["anna", "bob"]
    assert rep["has_large"] is False


if __name__ == "__main__":
    create_test_file()

    tests = [
        ("Проблема 1 (read_orders закрывает файл)", test_read_orders),
        ("Проблема 2 (totals_by_user затирает суммы)", test_totals_by_user),
        ("Проблема 3 (has_large_orders всегда True)", test_has_large_orders),
        ("Проблема 4 (vip_over_limit падает на None)", test_vip_over_limit),
        ("Проблема 5 (last_orders грузит весь файл)", test_last_orders_memory),
        ("Проблема 6 (build_report пустые totals)", test_build_report_totals),
    ]

    # Если запускают с системным аргументом, берем его, иначе тестируем оба
    modules_to_test = sys.argv[1:] if len(sys.argv) > 1 else ["report", "report_fixed"]

    for module_name in modules_to_test:
        print(f"Модуль: {module_name}.py")

        current_mod = importlib.import_module(module_name)

        failed = 0
        for name, func in tests:
            try:
                func(current_mod)
                print(f"[OK] {name}")
            except Exception as e:
                failed += 1
                print(f"[FAIL] {name}: {type(e).__name__}")

        print(f"\nИтог для {module_name}.py: успешно {len(tests) - failed} из {len(tests)}\n")
