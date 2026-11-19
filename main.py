"""퀴즈 게임 실행 파일: python main.py"""

import sys

from game import QuizGame


def main() -> None:
    # Windows 콘솔 등에서 이모지/한글 출력이 깨지지 않도록 UTF-8 로 맞춘다.
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    game = QuizGame()
    game.run()


if __name__ == "__main__":
    main()
