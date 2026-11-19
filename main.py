"""퀴즈 게임 실행 파일: python main.py"""

import sys
from pathlib import Path

from game import QuizGame

# 실행 위치와 상관없이 항상 프로젝트 루트의 state.json 을 사용한다.
STATE_PATH = Path(__file__).resolve().parent / "state.json"


def main() -> None:
    # Windows 콘솔 등에서 이모지/한글 출력이 깨지지 않도록 UTF-8 로 맞춘다.
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    game = QuizGame(STATE_PATH)
    game.run()


if __name__ == "__main__":
    main()
