# Задание 1 (обязательно). Мини-скрипт с обоснованным выбором коллекций
# Написать трекер книг/покупок/участников (тема на выбор — любая предметная область с «записями»), в котором сознательно использованы:
# • list — для меняющегося набора записей;
# • tuple — для фиксированной структуры одной записи (например (id, name, year));
# • dict — для быстрого поиска по ключу;
# • set — где важна только уникальность.
# К коду - короткий README.md (3–5 предложений), объясняющий, почему выбрана именно эта коллекция для каждого случая — это прямая тренировка перед аналогичным пунктом в чек-листе проекта на автомате. Код должен 100% избегать всех ловушек с семинара: никаких mutable default arguments, неосознанных alias’ов, list в качестве ключа и т.п.

class RecipeTracker:
    def __init__(self):
        self.recipes_list = []
        self.catalog = {}
        self.categories = set()

    def add_recipe(self, recipe_id: int, title: str, category: str, ingredients: list = None):
        ingredients = ingredients or []
        recipe_record = (recipe_id, title, category, tuple(ingredients))
        self.recipes_list.append(recipe_record)
        self.catalog[recipe_id] = recipe_record
        self.categories.add(category)

    def find_recipe(self, recipe_id: int):
        record = self.catalog.get(recipe_id)
        return record


tracker = RecipeTracker()

tracker.add_recipe(101, "Борщ", "Супы", ["Свекла", "Капуста"])
tracker.add_recipe(102, "Оливье", "Салаты", ["Горошек", "Картошка", "Колбаса"])
tracker.add_recipe(103, "Солянка", "Супы", ["Лимон", "Оливки", "Колбаса"])

print("Рецепты (list): ", tracker.recipes_list)
print("\nID рецептов (dict): ", tracker.catalog)
print("\nУникальные категории (set): ", tracker.categories)

olivie = tracker.find_recipe(102)
print("\nНайденный пецепт: ", olivie)

borch = tracker.find_recipe(101)
try:
    borch[3].append("Мясо")
except AttributeError as e:
    print("\nИнгредиенты - это кортеж (tuple), его нельзя изменить:", e)
print("\nРецепт борща (tuple): ", borch)
