"""단어 사전 적재와 조회."""

import os
from collections import defaultdict

from . import hangul

DEFAULT_WORDS_PATH = os.path.join(os.path.dirname(__file__), "words.txt")


class WordDictionary:
    """끝말잇기에 쓰이는 단어 모음."""

    def __init__(self, words):
        self._words = set()
        self._by_first = defaultdict(list)
        for word in words:
            self.add(word)

    @classmethod
    def from_file(cls, path=DEFAULT_WORDS_PATH):
        with open(path, encoding="utf-8") as f:
            lines = (line.strip() for line in f)
            return cls(line for line in lines if line and not line.startswith("#"))

    def add(self, word):
        """사전에 단어를 넣는다. 형식이 맞지 않으면 ValueError."""
        if len(word) < 2 or not hangul.is_hangul_word(word):
            raise ValueError(f"두 글자 이상의 한글 낱말이 아닙니다: {word!r}")
        if word not in self._words:
            self._words.add(word)
            self._by_first[word[0]].append(word)
        return word

    def __contains__(self, word):
        return word in self._words

    def __len__(self):
        return len(self._words)

    def __iter__(self):
        return iter(sorted(self._words))

    def starting_with(self, char, exclude=()):
        """해당 글자(두음법칙 포함)로 시작하는 단어 목록."""
        exclude = set(exclude)
        found = []
        for variant in sorted(hangul.dueum_variants(char)):
            found.extend(w for w in self._by_first[variant] if w not in exclude)
        return sorted(found)
