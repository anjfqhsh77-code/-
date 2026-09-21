import unittest

from wordchain import hangul


class DecomposeTest(unittest.TestCase):
    def test_decompose(self):
        self.assertEqual(hangul.decompose("각"), ("ㄱ", "ㅏ", "ㄱ"))
        self.assertEqual(hangul.decompose("가"), ("ㄱ", "ㅏ", ""))

    def test_compose_roundtrip(self):
        for ch in "가쾅힣뷁":
            self.assertEqual(hangul.compose(*hangul.decompose(ch)), ch)

    def test_decompose_rejects_non_syllable(self):
        with self.assertRaises(ValueError):
            hangul.decompose("A")

    def test_is_hangul_word(self):
        self.assertTrue(hangul.is_hangul_word("사과"))
        self.assertFalse(hangul.is_hangul_word("사과2"))
        self.assertFalse(hangul.is_hangul_word("ㄱㄴ"))
        self.assertFalse(hangul.is_hangul_word(""))


class DueumTest(unittest.TestCase):
    def test_rieul_to_nieun(self):
        self.assertEqual(hangul.dueum_variants("락"), {"락", "낙"})
        self.assertEqual(hangul.dueum_variants("로"), {"로", "노"})

    def test_rieul_to_ieung(self):
        self.assertEqual(hangul.dueum_variants("려"), {"려", "여"})
        self.assertEqual(hangul.dueum_variants("례"), {"례", "예"})
        self.assertEqual(hangul.dueum_variants("리"), {"리", "이"})

    def test_nieun_to_ieung(self):
        self.assertEqual(hangul.dueum_variants("녀"), {"녀", "여"})
        self.assertEqual(hangul.dueum_variants("뇨"), {"뇨", "요"})

    def test_nieun_with_other_vowel_unchanged(self):
        self.assertEqual(hangul.dueum_variants("나"), {"나"})

    def test_plain_syllable_unchanged(self):
        self.assertEqual(hangul.dueum_variants("과"), {"과"})


if __name__ == "__main__":
    unittest.main()
