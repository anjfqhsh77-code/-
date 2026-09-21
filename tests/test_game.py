import random
import unittest

from wordchain.dictionary import WordDictionary
from wordchain.game import EASY, HARD, NORMAL, Game, InvalidWord

WORDS = ["사과", "과일", "과자", "일기", "기차", "차표", "리본", "이사", "논리", "본전"]


def make_game(difficulty=NORMAL, words=WORDS, seed=0):
    return Game(WordDictionary(words), difficulty=difficulty, rng=random.Random(seed))


class DictionaryTest(unittest.TestCase):
    def test_rejects_short_word(self):
        with self.assertRaises(ValueError):
            WordDictionary(["가"])

    def test_rejects_non_hangul(self):
        with self.assertRaises(ValueError):
            WordDictionary(["apple"])

    def test_starting_with_includes_dueum(self):
        dictionary = WordDictionary(WORDS)
        self.assertEqual(dictionary.starting_with("리"), ["리본", "이사"])

    def test_starting_with_excludes_used(self):
        dictionary = WordDictionary(WORDS)
        self.assertEqual(dictionary.starting_with("과", exclude={"과자"}), ["과일"])

    def test_bundled_word_file_loads(self):
        dictionary = WordDictionary.from_file()
        self.assertGreater(len(dictionary), 100)
        self.assertIn("사과", dictionary)


class RuleTest(unittest.TestCase):
    def test_first_word_is_free(self):
        game = make_game()
        game.play("사과")
        self.assertEqual(game.next_char, "과")

    def test_must_follow_last_char(self):
        game = make_game()
        game.play("사과")
        with self.assertRaises(InvalidWord):
            game.play("기차")

    def test_dueum_is_allowed(self):
        game = make_game()
        game.play("논리")
        game.play("이사")  # 리 -> 이
        self.assertEqual(game.history, ["논리", "이사"])

    def test_rejects_repeat(self):
        game = make_game()
        game.play("사과")
        game.play("과일")
        game.play("일기")
        game.play("기차")
        game.play("차표")
        with self.assertRaises(InvalidWord):
            game.play("표")

    def test_rejects_used_word(self):
        game = make_game(words=["사과", "과사", "사슴"])
        game.play("사과")
        game.play("과사")
        with self.assertRaises(InvalidWord) as ctx:
            game.play("사과")
        self.assertIn("이미 나온", str(ctx.exception))

    def test_rejects_unknown_word(self):
        game = make_game()
        with self.assertRaises(InvalidWord) as ctx:
            game.play("없는말")
        self.assertIn("사전에 없는", str(ctx.exception))

    def test_rejects_one_letter(self):
        game = make_game()
        with self.assertRaises(InvalidWord):
            game.play("과")

    def test_invalid_word_is_not_recorded(self):
        game = make_game()
        with self.assertRaises(InvalidWord):
            game.play("없는말")
        self.assertEqual(game.history, [])


class ComputerTest(unittest.TestCase):
    def test_returns_none_when_stuck(self):
        game = make_game(words=["사과", "과일"])
        game.play("사과")
        game.play("과일")
        self.assertIsNone(game.choose_computer_word())

    def test_choice_follows_rules(self):
        game = make_game()
        game.play("사과")
        word = game.choose_computer_word()
        self.assertIn(word, ["과일", "과자"])

    def test_hard_mode_picks_dead_end(self):
        # '과자'로 이으면 상대가 '자'로 시작할 단어가 없다.
        game = make_game(difficulty=HARD)
        game.play("사과")
        self.assertEqual(game.choose_computer_word(), "과자")

    def test_easy_mode_keeps_game_going(self):
        game = make_game(difficulty=EASY)
        game.play("사과")
        self.assertEqual(game.choose_computer_word(), "과일")

    def test_hint_is_playable(self):
        game = make_game()
        game.play("사과")
        game.play(game.hint())

    def test_hint_is_none_when_stuck(self):
        game = make_game(words=["사과", "과일"])
        game.play("사과")
        game.play("과일")
        self.assertIsNone(game.hint())


class CliTest(unittest.TestCase):
    def test_parser_defaults(self):
        from wordchain.cli import build_parser

        args = build_parser().parse_args([])
        self.assertEqual(args.difficulty, NORMAL)
        self.assertEqual(args.first, "me")


if __name__ == "__main__":
    unittest.main()
