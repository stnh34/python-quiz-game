"""게임 전체 흐름을 관리하는 QuizGame 클래스."""

import random
from pathlib import Path

from default_quizzes import create_default_quizzes
from input_handler import HINT_COMMAND, InputHandler
from quiz import Quiz
from score_board import HINT_PENALTY, ScoreBoard
from storage import StateCorruptedError, StateStorage

LINE = "=" * 40
SUB_LINE = "-" * 40


class QuizGame:
    """메뉴를 보여주고 퀴즈 풀기/추가/목록/점수/삭제/저장 기능을 조율한다.

    - 입력 검증: InputHandler
    - 점수/기록: ScoreBoard
    - 파일 입출력: StateStorage
    """

    MENU_ITEMS = ("퀴즈 풀기", "퀴즈 추가", "퀴즈 목록", "점수 확인", "퀴즈 삭제", "종료")

    def __init__(self, state_path: Path):
        self.inputs = InputHandler()
        self.storage = StateStorage(state_path)
        self.quizzes: list[Quiz] = create_default_quizzes()
        self.scores = ScoreBoard()

    # ------------------------------------------------------------------
    # 메인 루프
    # ------------------------------------------------------------------
    def run(self) -> None:
        """프로그램 진입점. Ctrl+C / 입력 종료(EOF)에도 안전하게 끝낸다."""
        self.print_title()
        self.load_state()
        try:
            while True:
                self.show_menu()
                choice = self.inputs.read_int("선택: ", 1, len(self.MENU_ITEMS))
                if choice == len(self.MENU_ITEMS):
                    self.exit_game()
                    break
                self.handle_menu(choice)
        except (KeyboardInterrupt, EOFError):
            print("\n\n⚠️ 입력이 중단되었습니다. 안전하게 종료합니다.")
            self.on_interrupt()

    def print_title(self) -> None:
        print(LINE)
        print("        🎯 나만의 퀴즈 게임 🎯")
        print(LINE)

    def show_menu(self) -> None:
        print()
        print(LINE)
        for number, label in enumerate(self.MENU_ITEMS, start=1):
            print(f"{number}. {label}")
        print(LINE)

    def handle_menu(self, choice: int) -> None:
        actions = {
            1: self.play_quiz,
            2: self.add_quiz,
            3: self.list_quizzes,
            4: self.show_score,
            5: self.delete_quiz,
        }
        actions[choice]()

    # ------------------------------------------------------------------
    # 퀴즈 풀기
    # ------------------------------------------------------------------
    def play_quiz(self) -> None:
        """퀴즈를 무작위로 출제하고 결과/최고 점수를 저장한다."""
        if not self.quizzes:
            print("\n📭 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        selected = self.choose_questions()
        total = len(selected)
        print(f"\n📝 퀴즈를 시작합니다! (총 {total}문제)")
        print(f"💡 힌트가 있는 문제는 'h' 를 입력하면 힌트를 볼 수 있습니다. "
              f"(사용 시 -{HINT_PENALTY}점)")

        correct_count = 0
        hints_used = 0
        for number, quiz in enumerate(selected, start=1):
            print()
            print(SUB_LINE)
            quiz.display(number)
            is_correct, used_hint = self.ask_answer(quiz)
            hints_used += used_hint
            if is_correct:
                correct_count += 1
                print("✅ 정답입니다!")
            else:
                print(f"❌ 오답입니다. 정답은 {quiz.correct_choice_text()} 입니다.")

        score = ScoreBoard.calculate_score(correct_count, total, hints_used)
        is_new_best = self.scores.record_game(total, correct_count, hints_used, score)
        self.save_state()
        self.print_result(total, correct_count, hints_used, score, is_new_best)

    def choose_questions(self) -> list[Quiz]:
        """풀 문제 수를 입력받고, 원본 순서는 유지한 채 무작위로 뽑는다."""
        available = len(self.quizzes)
        print()
        count = self.inputs.read_int(f"몇 문제를 풀까요? (1-{available}): ", 1, available)
        return random.sample(self.quizzes, count)

    def ask_answer(self, quiz: Quiz) -> tuple[bool, bool]:
        """정답을 입력받는다. (정답 여부, 힌트 사용 여부)를 반환한다."""
        used_hint = False
        while True:
            hint_available = quiz.has_hint() and not used_hint
            prompt = "정답 입력 (힌트: h): " if hint_available else "정답 입력: "
            user_answer = self.inputs.read_int(
                prompt, 1, Quiz.CHOICE_COUNT, allow_hint=hint_available
            )
            if user_answer == HINT_COMMAND:
                used_hint = True
                print(f"💡 힌트: {quiz.hint}")
                continue
            return quiz.is_correct(user_answer), used_hint

    @staticmethod
    def print_result(total: int, correct_count: int, hints_used: int,
                     score: int, is_new_best: bool) -> None:
        print()
        print(LINE)
        print(f"🏆 결과: {total}문제 중 {correct_count}문제 정답! ({score}점)")
        if hints_used:
            print(f"💡 힌트 {hints_used}회 사용 (-{hints_used * HINT_PENALTY}점 반영)")
        if is_new_best:
            print("🎉 새로운 최고 점수입니다!")
        print(LINE)

    # ------------------------------------------------------------------
    # 퀴즈 관리 (추가 / 목록 / 삭제) 및 점수 확인
    # ------------------------------------------------------------------
    def add_quiz(self) -> None:
        """문제, 선택지 4개, 정답 번호, 힌트(선택)를 입력받아 등록하고 저장한다."""
        print("\n📌 새로운 퀴즈를 추가합니다.")
        print()
        question = self.inputs.read_text("문제를 입력하세요: ")
        choices = [
            self.inputs.read_text(f"선택지 {number}: ")
            for number in range(1, Quiz.CHOICE_COUNT + 1)
        ]
        answer = self.inputs.read_int(
            f"정답 번호 (1-{Quiz.CHOICE_COUNT}): ", 1, Quiz.CHOICE_COUNT
        )
        hint = input("힌트 (없으면 Enter): ").strip()

        self.quizzes.append(Quiz(question, choices, answer, hint))
        if self.save_state():
            print("\n✅ 퀴즈가 추가되었습니다!")
        else:
            print("\n⚠️ 퀴즈는 추가되었지만 파일 저장에 실패했습니다.")

    def list_quizzes(self) -> bool:
        """등록된 퀴즈 목록을 출력한다. 퀴즈가 없으면 False 를 반환한다."""
        if not self.quizzes:
            print("\n📭 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return False

        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print()
        print(SUB_LINE)
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"[{number}] {quiz.question}")
        print(SUB_LINE)
        return True

    def delete_quiz(self) -> None:
        """번호를 골라 퀴즈를 삭제하고 파일에 반영한다. 0 입력 시 취소."""
        if not self.list_quizzes():
            return

        count = len(self.quizzes)
        number = self.inputs.read_int(f"삭제할 퀴즈 번호 (1-{count}, 취소: 0): ", 0, count)
        if number == 0:
            print("↩️ 삭제를 취소했습니다.")
            return

        target = self.quizzes[number - 1]
        if not self.inputs.confirm(f"'{target.question}' 퀴즈를 삭제할까요? (y/n): "):
            print("↩️ 삭제를 취소했습니다.")
            return

        self.quizzes.pop(number - 1)
        if self.save_state():
            print("🗑️ 퀴즈를 삭제했습니다.")
        else:
            print("⚠️ 퀴즈는 삭제되었지만 파일 저장에 실패했습니다.")

    def show_score(self) -> None:
        """최고 점수와 최근 기록을 보여준다."""
        self.scores.display()

    # ------------------------------------------------------------------
    # 종료
    # ------------------------------------------------------------------
    def exit_game(self) -> None:
        if self.save_state():
            print("\n💾 데이터를 저장했습니다.")
        print("👋 게임을 종료합니다. 다음에 또 만나요!")

    def on_interrupt(self) -> None:
        """Ctrl+C / EOF 로 중단되었을 때 가능한 범위에서 저장한다."""
        if self.save_state():
            print("💾 현재까지의 데이터를 저장했습니다.")

    # ------------------------------------------------------------------
    # 파일 저장/불러오기 (state.json)
    # ------------------------------------------------------------------
    def load_state(self) -> None:
        """state.json 을 불러온다. 없거나 손상되었으면 기본 데이터로 시작한다."""
        try:
            data = self.storage.load()
            if data is None:
                print("📂 저장된 데이터가 없어 기본 퀴즈로 시작합니다.")
                self.reset_to_defaults()
                self.save_state()
                return
            self.apply_state(data)
        except (StateCorruptedError, ValueError, TypeError) as error:
            print(f"⚠️ 데이터 파일이 손상되었습니다. ({error})")
            backup = self.storage.backup_corrupted()
            if backup is not None:
                print(f"   손상된 파일은 {backup.name} 으로 보관했습니다.")
            print("   기본 퀴즈 데이터로 복구합니다.")
            self.reset_to_defaults()
            self.save_state()
            return

        print(f"📂 저장된 데이터를 불러왔습니다. "
              f"(퀴즈 {len(self.quizzes)}개, 최고점수 {self.scores.best_text()})")

    def save_state(self) -> bool:
        """현재 상태를 state.json 에 저장한다. 성공하면 True."""
        try:
            self.storage.save(self.to_state())
        except OSError as error:
            print(f"⚠️ 데이터를 저장하지 못했습니다: {error}")
            return False
        return True

    def reset_to_defaults(self) -> None:
        self.quizzes = create_default_quizzes()
        self.scores = ScoreBoard()

    def to_state(self) -> dict:
        """저장할 데이터를 JSON 으로 바꿀 수 있는 dict 로 만든다."""
        return {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            **self.scores.to_dict(),
        }

    def apply_state(self, data: dict) -> None:
        """불러온 dict 를 검증한 뒤 반영한다. 형식이 틀리면 ValueError."""
        raw_quizzes = data.get("quizzes")
        if not isinstance(raw_quizzes, list):
            raise ValueError("'quizzes' 항목이 목록이 아닙니다.")
        quizzes = [Quiz.from_dict(item) for item in raw_quizzes]
        scores = ScoreBoard.from_dict(data)

        # 모든 검증을 통과한 뒤에 한꺼번에 반영한다.
        self.quizzes = quizzes
        self.scores = scores
