# 끝말잇기 (wordchain)

파이썬으로 만든 한글 끝말잇기 게임입니다. 컴퓨터와 번갈아 단어를 이어 갑니다.
표준 라이브러리만 쓰므로 따로 설치할 것은 없습니다. (Python 3.8 이상)

## 실행

```bash
python3 -m wordchain
```

옵션

| 옵션 | 설명 | 기본값 |
| --- | --- | --- |
| `-d, --difficulty {easy,normal,hard}` | 컴퓨터 실력 | `normal` |
| `-f, --first {me,computer}` | 누가 먼저 시작할지 | `me` |
| `-t, --time-limit 초` | 한 수당 제한 시간 (0이면 제한 없음) | `0` |
| `-w, --words 경로` | 단어 사전 파일 | `wordchain/words.txt` |
| `--seed 숫자` | 같은 판을 다시 돌려 볼 때 쓰는 난수 시드 | 없음 |

예) 어려움 난이도로 컴퓨터가 먼저 시작, 한 수당 10초:

```bash
python3 -m wordchain -d hard -f computer -t 10
```

게임 중에는 `/힌트`, `/기록`, `/도움말`, `/포기` 명령을 쓸 수 있습니다.

## 규칙

- 두 글자 이상의 한글 낱말만 쓸 수 있습니다.
- 앞말의 끝 글자로 시작해야 합니다.
- 두음법칙을 허용합니다. 예를 들어 `보리` 다음에는 `리본`도 `이불`도 됩니다.
  - ㄹ + ㅑㅕㅛㅠㅣ 계열 → ㅇ (례 → 예, 리 → 이)
  - ㄹ + 그 밖의 모음 → ㄴ (락 → 낙, 로 → 노)
  - ㄴ + ㅑㅕㅛㅠㅣ 계열 → ㅇ (녀 → 여, 뇨 → 요)
  - 반대 방향(`여` 다음에 `려`)은 인정하지 않습니다.
- 이미 나온 단어는 다시 쓸 수 없습니다.
- 사전에 있는 단어만 인정합니다. 이을 단어를 내지 못하면 집니다.

난이도별로 컴퓨터가 단어를 고르는 방식이 다릅니다.

- `easy` — 상대가 이어 가기 쉬운 단어를 고릅니다.
- `normal` — 가능한 단어 중 무작위로 고릅니다.
- `hard` — 상대가 받을 수 있는 단어가 가장 적은 쪽으로 몰아갑니다.

## 단어 사전

기본 사전은 `wordchain/words.txt`에 들어 있는 341개 낱말입니다.
한 줄에 한 낱말씩 적으면 되고, `#`으로 시작하는 줄은 주석입니다.
단어를 직접 추가하거나, 따로 만든 파일을 `--words` 옵션으로 지정해 쓸 수 있습니다.

## 구조

```
wordchain/
  hangul.py      한글 음절 분해·조합, 두음법칙
  dictionary.py  단어 사전 적재와 조회
  game.py        규칙 판정, 진행 상태, 컴퓨터 수 선택
  cli.py         명령줄 실행부
  words.txt      기본 단어 사전
tests/           단위 테스트
```

게임 로직은 화면 출력과 분리돼 있어 다른 곳에서 가져다 쓸 수 있습니다.

```python
from wordchain import Game, WordDictionary

game = Game(WordDictionary.from_file(), difficulty="hard")
game.play("사과")
print(game.choose_computer_word())
```

## 테스트

```bash
python3 -m unittest discover -s tests -t .
```
