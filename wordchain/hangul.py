"""한글 음절 분해/조합과 두음법칙 처리."""

BASE = 0xAC00
LAST = 0xD7A3

CHOSEONG = (
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ",
)
JUNGSEONG = (
    "ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ",
    "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ",
)
JONGSEONG = (
    "", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ",
    "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ",
)

# 두음법칙에서 'ㅇ'으로 바뀌는 모음(ㅑ·ㅕ·ㅛ·ㅠ·ㅣ 계열)
I_VOWELS = frozenset("ㅑㅒㅕㅖㅛㅠㅣ")


def is_syllable(ch):
    """완성형 한글 음절이면 True."""
    return len(ch) == 1 and BASE <= ord(ch) <= LAST


def is_hangul_word(word):
    """모든 글자가 완성형 한글이면 True."""
    return bool(word) and all(is_syllable(ch) for ch in word)


def decompose(ch):
    """음절을 (초성, 중성, 종성) 문자열 튜플로 분해한다."""
    if not is_syllable(ch):
        raise ValueError(f"완성형 한글이 아닙니다: {ch!r}")
    code = ord(ch) - BASE
    return CHOSEONG[code // 588], JUNGSEONG[(code % 588) // 28], JONGSEONG[code % 28]


def compose(cho, jung, jong=""):
    """(초성, 중성, 종성)을 하나의 음절로 조합한다."""
    return chr(
        BASE
        + CHOSEONG.index(cho) * 588
        + JUNGSEONG.index(jung) * 28
        + JONGSEONG.index(jong)
    )


def dueum_variants(ch):
    """글자에 두음법칙을 적용했을 때 허용되는 첫 글자들.

    ㄹ + ㅑㅕㅛㅠㅣ 계열 -> ㅇ (례->예, 리->이)
    ㄹ + 그 밖의 모음    -> ㄴ (락->낙, 로->노)
    ㄴ + ㅑㅕㅛㅠㅣ 계열 -> ㅇ (녀->여, 뇨->요)
    """
    variants = {ch}
    cho, jung, jong = decompose(ch)
    if cho == "ㄹ":
        variants.add(compose("ㅇ" if jung in I_VOWELS else "ㄴ", jung, jong))
    elif cho == "ㄴ" and jung in I_VOWELS:
        variants.add(compose("ㅇ", jung, jong))
    return variants
