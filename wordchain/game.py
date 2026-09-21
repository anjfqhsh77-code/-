"""끝말잇기 규칙과 진행 상태."""

import random

from . import hangul

EASY, NORMAL, HARD = "easy", "normal", "hard"
DIFFICULTIES = (EASY, NORMAL, HARD)
DIFFICULTY_LABELS = {EASY: "쉬움", NORMAL: "보통", HARD: "어려움"}


class InvalidWord(Exception):
    """규칙에 어긋난 단어."""


class Game:
    """한 판의 진행 상태를 들고 있는 객체.

    규칙
      - 두 글자 이상의 한글 낱말만 쓴다.
      - 앞말의 끝 글자로 시작해야 하며, 두음법칙을 허용한다.
      - 이미 나온 단어는 다시 쓸 수 없다.
      - 이을 단어를 내지 못하면 진다.
    """

    def __init__(self, dictionary, difficulty=NORMAL, rng=None):
        if difficulty not in DIFFICULTIES:
            raise ValueError(f"알 수 없는 난이도: {difficulty}")
        self.dictionary = dictionary
        self.difficulty = difficulty
        self.rng = rng or random.Random()
        self.history = []
        self.used = set()

    @property
    def last_word(self):
        return self.history[-1] if self.history else None

    @property
    def next_char(self):
        """다음 단어가 시작해야 할 글자. 첫 수라면 None."""
        return self.history[-1][-1] if self.history else None

    def allowed_first_chars(self):
        """다음 단어에 쓸 수 있는 첫 글자들(두음법칙 포함)."""
        if self.next_char is None:
            return set()
        return hangul.dueum_variants(self.next_char)

    def check(self, word):
        """규칙 위반이면 InvalidWord를 던진다."""
        if len(word) < 2:
            raise InvalidWord("두 글자 이상이어야 합니다.")
        if not hangul.is_hangul_word(word):
            raise InvalidWord("한글 낱말만 쓸 수 있습니다.")
        if word in self.used:
            raise InvalidWord(f"'{word}'은(는) 이미 나온 단어입니다.")
        if word not in self.dictionary:
            raise InvalidWord(f"'{word}'은(는) 사전에 없는 단어입니다.")
        allowed = self.allowed_first_chars()
        if allowed and word[0] not in allowed:
            expected = " 또는 ".join(f"'{c}'" for c in sorted(allowed))
            raise InvalidWord(f"{expected}(으)로 시작해야 합니다.")

    def play(self, word):
        """단어를 한 수 둔다. 규칙 위반이면 InvalidWord."""
        self.check(word)
        self.history.append(word)
        self.used.add(word)
        return word

    def candidates(self):
        """지금 낼 수 있는 단어 목록."""
        if self.next_char is None:
            return sorted(w for w in self.dictionary if w not in self.used)
        return self.dictionary.starting_with(self.next_char, exclude=self.used)

    def hint(self):
        """낼 수 있는 단어 하나. 없으면 None."""
        options = self.candidates()
        return self.rng.choice(options) if options else None

    def choose_computer_word(self):
        """난이도에 맞춰 컴퓨터가 낼 단어를 고른다. 없으면 None."""
        options = self.candidates()
        if not options:
            return None
        if self.difficulty == EASY:
            # 상대가 이어 가기 쉬운 단어를 고른다.
            return max(options, key=self._reply_count)
        if self.difficulty == NORMAL:
            return self.rng.choice(options)
        # 어려움: 상대가 받을 수 있는 단어가 가장 적은 쪽으로 몰아간다.
        fewest = min(self._reply_count(w) for w in options)
        return self.rng.choice([w for w in options if self._reply_count(w) == fewest])

    def _reply_count(self, word):
        """그 단어를 냈을 때 상대가 쓸 수 있는 단어 수."""
        used = self.used | {word}
        return len(self.dictionary.starting_with(word[-1], exclude=used))
