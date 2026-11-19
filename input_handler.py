"""사용자 입력을 받고 검증하는 InputHandler 클래스."""

HINT_COMMAND = "hint"
_HINT_WORDS = ("h", "hint", "힌트")


class InputHandler:
    """공통 입력/예외 처리 기준을 한 곳에서 담당한다.

    - 입력 앞뒤 공백 제거
    - 빈 입력, 숫자 변환 실패, 허용 범위 밖 숫자 → 안내 후 재입력
    - KeyboardInterrupt / EOFError 는 호출한 쪽(QuizGame.run)에서 처리하도록 그대로 전달
    """

    def read_text(self, prompt: str) -> str:
        """비어 있지 않은 문자열을 입력받아 반환한다."""
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("⚠️ 빈 입력입니다. 내용을 입력하세요.")

    def read_int(self, prompt: str, min_value: int, max_value: int,
                 allow_hint: bool = False) -> int | str:
        """min_value ~ max_value 범위의 정수를 입력받아 반환한다.

        allow_hint 가 True 이면 'h' / 'hint' / '힌트' 입력 시 HINT_COMMAND 를 반환한다.
        """
        range_message = f"{min_value}-{max_value} 사이의 숫자를 입력하세요."
        while True:
            raw = input(prompt).strip()

            if raw == "":
                print(f"⚠️ 입력이 비어 있습니다. {range_message}")
                continue

            if allow_hint and raw.lower() in _HINT_WORDS:
                return HINT_COMMAND

            try:
                number = int(raw)
            except ValueError:
                print(f"⚠️ 잘못된 입력입니다. {range_message}")
                continue

            if not min_value <= number <= max_value:
                print(f"⚠️ 잘못된 입력입니다. {range_message}")
                continue

            return number

    def confirm(self, prompt: str) -> bool:
        """y/n 질문을 하고 y 이면 True 를 반환한다."""
        while True:
            value = input(prompt).strip().lower()
            if value in ("y", "yes", "예", "ㅇ"):
                return True
            if value in ("n", "no", "아니오", "ㄴ"):
                return False
            print("⚠️ y 또는 n 을 입력하세요.")
