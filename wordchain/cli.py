"""끝말잇기 명령줄 실행부."""

import argparse
import random
import sys
import time

from .dictionary import DEFAULT_WORDS_PATH, WordDictionary
from .game import DIFFICULTIES, DIFFICULTY_LABELS, NORMAL, Game, InvalidWord

HELP_TEXT = """\
명령어
  /힌트     낼 수 있는 단어를 하나 알려 줍니다
  /기록     지금까지 나온 단어를 보여 줍니다
  /도움말   이 안내를 다시 봅니다
  /포기     이번 판을 포기합니다
"""


def build_parser():
    parser = argparse.ArgumentParser(
        prog="wordchain",
        description="한글 끝말잇기 게임 (두음법칙 허용)",
    )
    parser.add_argument(
        "-d", "--difficulty", choices=DIFFICULTIES, default=NORMAL,
        help="컴퓨터 실력 (기본값: normal)",
    )
    parser.add_argument(
        "-w", "--words", default=DEFAULT_WORDS_PATH,
        help="단어 사전 파일 경로",
    )
    parser.add_argument(
        "-f", "--first", choices=("me", "computer"), default="me",
        help="누가 먼저 시작할지 (기본값: me)",
    )
    parser.add_argument(
        "-t", "--time-limit", type=float, default=0,
        help="한 수당 제한 시간(초). 0이면 제한 없음",
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="같은 판을 다시 돌려 볼 때 쓰는 난수 시드",
    )
    return parser


def prompt(game):
    """사람 차례의 입력을 받아 (입력값, 걸린 시간)으로 돌려준다."""
    head = f"[{game.next_char}] " if game.next_char else ""
    started = time.monotonic()
    answer = input(f"{head}나: ").strip()
    return answer, time.monotonic() - started


def play_turn(game, args):
    """사람 차례. 계속하면 True, 판이 끝나면 False."""
    while True:
        try:
            answer, elapsed = prompt(game)
        except (EOFError, KeyboardInterrupt):
            print("\n게임을 끝냅니다.")
            return False

        if not answer:
            continue
        if answer in ("/포기", "/그만", "/quit"):
            print(f"포기했습니다. 컴퓨터가 이겼습니다. (총 {len(game.history)}수)")
            return False
        if answer in ("/도움말", "/help"):
            print(HELP_TEXT)
            continue
        if answer in ("/기록", "/history"):
            print(format_history(game))
            continue
        if answer in ("/힌트", "/hint"):
            word = game.hint()
            print(f"  힌트: {word}" if word else "  낼 수 있는 단어가 없습니다.")
            continue

        if args.time_limit and elapsed > args.time_limit:
            print(f"시간 초과({elapsed:.1f}초). 컴퓨터가 이겼습니다.")
            return False

        try:
            game.play(answer)
        except InvalidWord as error:
            print(f"  {error} 다시 입력하세요.")
            continue
        return True


def play_computer_turn(game):
    """컴퓨터 차례. 계속하면 True, 판이 끝나면 False."""
    word = game.choose_computer_word()
    if word is None:
        print(f"컴퓨터가 이을 단어를 찾지 못했습니다. 당신이 이겼습니다! (총 {len(game.history)}수)")
        return False
    game.play(word)
    print(f"컴퓨터: {word}")
    return True


def format_history(game):
    if not game.history:
        return "  아직 나온 단어가 없습니다."
    return "  " + " → ".join(game.history)


def run(args):
    try:
        dictionary = WordDictionary.from_file(args.words)
    except OSError as error:
        print(f"사전 파일을 읽지 못했습니다: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"사전 파일에 잘못된 단어가 있습니다: {error}", file=sys.stderr)
        return 1

    game = Game(dictionary, difficulty=args.difficulty, rng=random.Random(args.seed))

    print("끝말잇기를 시작합니다.")
    print(f"  난이도: {DIFFICULTY_LABELS[args.difficulty]} / 사전: {len(dictionary)}개 단어")
    if args.time_limit:
        print(f"  제한 시간: 한 수당 {args.time_limit:g}초")
    print(HELP_TEXT)

    computer_turn = args.first == "computer"
    while True:
        if computer_turn:
            alive = play_computer_turn(game)
        elif not game.candidates():
            print(f"사전에 이을 단어가 남지 않았습니다. 컴퓨터가 이겼습니다. (총 {len(game.history)}수)")
            alive = False
        else:
            alive = play_turn(game, args)
        if not alive:
            break
        computer_turn = not computer_turn

    print(f"기록: {' → '.join(game.history)}" if game.history else "기록 없음")
    return 0


def main(argv=None):
    return run(build_parser().parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
