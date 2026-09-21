"""한글 끝말잇기 게임."""

from .dictionary import WordDictionary
from .game import Game, InvalidWord

__all__ = ["WordDictionary", "Game", "InvalidWord"]
__version__ = "1.0.0"
