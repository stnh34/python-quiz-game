"""개별 퀴즈 하나를 표현하는 Quiz 클래스."""


class Quiz:
    """문제(question), 선택지(choices), 정답 번호(answer, 1~4), 힌트(hint)를 가진다."""

    CHOICE_COUNT = 4

    def __init__(self, question: str, choices: list[str], answer: int, hint: str = ""):
        question = str(question).strip()
        if not question:
            raise ValueError("문제가 비어 있습니다.")
        if not isinstance(choices, list) or len(choices) != self.CHOICE_COUNT:
            raise ValueError(f"선택지는 {self.CHOICE_COUNT}개여야 합니다.")
        choices = [str(choice).strip() for choice in choices]
        if any(not choice for choice in choices):
            raise ValueError("비어 있는 선택지가 있습니다.")
        # bool 은 int 의 하위 타입이므로 명시적으로 제외한다.
        if isinstance(answer, bool) or not isinstance(answer, int) \
                or not 1 <= answer <= self.CHOICE_COUNT:
            raise ValueError(f"정답은 1~{self.CHOICE_COUNT} 사이의 번호여야 합니다.")

        self.question = question
        self.choices = choices
        self.answer = answer
        self.hint = str(hint or "").strip()

    def display(self, number: int | None = None) -> None:
        """문제와 선택지를 화면에 출력한다."""
        title = f"[문제 {number}]" if number is not None else "[문제]"
        print(title)
        print(self.question)
        print()
        for index, choice in enumerate(self.choices, start=1):
            print(f"{index}. {choice}")
        print()

    def is_correct(self, user_answer: int) -> bool:
        """사용자가 고른 번호가 정답인지 확인한다."""
        return user_answer == self.answer

    def has_hint(self) -> bool:
        return bool(self.hint)

    def correct_choice_text(self) -> str:
        """정답 번호와 내용을 '3. 6개' 형태로 돌려준다."""
        return f"{self.answer}. {self.choices[self.answer - 1]}"

    def to_dict(self) -> dict:
        """JSON 저장을 위해 딕셔너리로 변환한다."""
        return {
            "question": self.question,
            "choices": list(self.choices),
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Quiz":
        """딕셔너리(JSON)에서 Quiz 객체를 만든다. 형식이 틀리면 ValueError."""
        if not isinstance(data, dict):
            raise ValueError("퀴즈 데이터 형식이 올바르지 않습니다.")
        try:
            return cls(data["question"], data["choices"], data["answer"], data.get("hint", ""))
        except KeyError as error:
            raise ValueError(f"퀴즈 데이터에 {error} 항목이 없습니다.") from error

    def __repr__(self) -> str:
        return f"Quiz(question={self.question!r}, answer={self.answer})"
