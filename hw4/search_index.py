# Задание 3. Поисковый индекс
# В файле `hw4/search_index.py` реализуйте класс `SearchIndex`: простую поисковую систему по текстовым документам
# на основе **инвертированного индекса** (словарь «слово -> множество id документов»). Так устроен поиск
# в поисковиках, IDE и базах данных.
# Требования:
# - `add(doc_id, text)` добавляет документ. Слова приводятся к нижнему регистру, разделители и знаки препинания
#   отбрасываются (используйте `re.findall(r'\w+', text.lower())`). Повторное добавление того же `doc_id`
#   заменяет старый текст;
# - `search_all(*words)` возвращает множество id документов, в которых есть **все** слова;
# - `search_any(*words)` возвращает множество id документов, в которых есть **хотя бы одно** слово;
# - `remove(doc_id)` удаляет документ из индекса; слово, которое больше не встречается ни в одном документе,
#   должно исчезнуть из индекса полностью;
# - `top_words(n)` возвращает `n` самых частых слов по всем документам в виде списка пар `(слово, количество)`;
# - поиск по словам не должен перебирать все документы: сложность `search_*` зависит от числа слов в запросе
#   и размера найденных множеств, а не от общего числа документов.
# Подумайте, какие структуры данных хранить, чтобы `remove` и повторный `add` работали без перебора всего индекса.
# Выбор коротко обоснуйте в docstring класса.


import re
from collections import Counter


class SearchIndex:
    """
    1. _inverted_index: dict[str, set[int]] - классический инвертированный индекс.
       Дает доступ к множеству документов по слову за O(1), позволяя быстро пересекать множества.
    2. _doc_words: dict[int, list[str]] - прямой индекс (doc_id -> список слов).
       Позволяет методу remove() мгновенно узнать, какие слова нужно удалить из инвертированного 
       индекса для конкретного документа, не перебирая все слова в базе.
    3. _global_counts: Counter - счетчик частоты слов по всем документам.
       Позволяет методу top_words(n) возвращать топ слов моментально, без пересчета всего индекса.
    """

    def __init__(self):
        self._inverted_index = {}
        self._doc_words = {}
        self._global_counts = Counter()

    def add(self, doc_id: int, text: str) -> None:
        if doc_id in self._doc_words:
            self.remove(doc_id)

        words = re.findall(r'\w+', text.lower())

        self._doc_words[doc_id] = words

        for word in words:
            if word not in self._inverted_index:
                self._inverted_index[word] = set()
            self._inverted_index[word].add(doc_id)
            self._global_counts[word] += 1

    def remove(self, doc_id: int) -> None:
        if doc_id not in self._doc_words:
            return

        words = self._doc_words.pop(doc_id)

        for word in words:
            self._global_counts[word] -= 1
            if self._global_counts[word] == 0:
                del self._global_counts[word]

            if word in self._inverted_index:
                self._inverted_index[word].discard(doc_id)
                if not self._inverted_index[word]:
                    del self._inverted_index[word]

    def search_all(self, *words: str) -> set:
        words = [w.lower() for w in words]
        if not words:
            return set()

        if words[0] not in self._inverted_index:
            return set()

        result = set(self._inverted_index[words[0]])

        for word in words[1:]:
            if word not in self._inverted_index:
                return set()
            result.intersection_update(self._inverted_index[word])

        return result

    def search_any(self, *words: str) -> set:
        result = set()

        for word in words:
            word = word.lower()
            if word in self._inverted_index:
                result.update(self._inverted_index[word])

        return result

    def top_words(self, n: int) -> list:
        return self._global_counts.most_common(n)


if __name__ == '__main__':
    idx = SearchIndex()
    idx.add(1, 'Python is a programming language.')
    idx.add(2, 'A dict is a hash table; a set is a hash table too!')
    idx.add(3, 'Python dict and set are fast.')
    assert idx.search_all('python') == {1, 3}
    assert idx.search_all('dict', 'set') == {2, 3}
    assert idx.search_all('python', 'hash') == set()
    assert idx.search_any('language', 'fast') == {1, 3}
    assert idx.search_all('PYTHON') == {1, 3}
    assert idx.search_all('nothing') == set()
    assert idx.top_words(2) == [('a', 5), ('is', 3)]
    idx.remove(1)
    assert idx.search_all('python') == {3}
    assert idx.search_any('language', 'programming') == set()
    idx.add(3, 'Totally new text')
    assert idx.search_all('python') == set()
    assert idx.search_all('new') == {3}
