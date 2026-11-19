"""게임 전체 흐름을 관리하는 QuizGame 클래스."""

import random
from pathlib import Path

from default_quizzes import create_default_quizzes
from input_handler import InputHandler
from quiz import Quiz
from storage import StateCorruptedError, StateStorage

LINE = "=" * 40
SUB_LINE = "-" * 40


class QuizGame:
    """메뉴 표시와 각 기능 실행을 담당한다."""

    MENU_ITEMS = ("퀴즈 풀기", "퀴즈 추가", "퀴즈 목록", "점수 확인", "퀴즈 삭제", "종료")

    def __init__(self, state_path: Path):
        self.inputs = InputHandler()
        self.storage = StateStorage(state_path)
        self.quizzes: list[Quiz] = create_default_quizzes()
        self.best_score: int | None = None        # 아직 풀지 않았으면 None
        self.best_detail: dict | None = None      # {"correct": 4, "total": 5}
        self.history: list[dict] = []             # 게임 기록 (보너스)

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
    # 기능
    # ------------------------------------------------------------------
    def play_quiz(self) -> None:
        """저장된 퀴즈를 순서대로 출제하고 결과를 보여준다."""
        if not self.quizzes:
            print("\n📭 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        available = len(self.quizzes)
        print()
        total = self.inputs.read_int(f"몇 문제를 풀까요? (1-{available}): ", 1, available)
        # 원본 목록은 그대로 두고, 무작위로 total 개를 뽑아 순서를 섞는다.
        selected = random.sample(self.quizzes, total)
        print(f"\n📝 퀴즈를 시작합니다! (총 {total}문제)")

        correct_count = 0
        for number, quiz in enumerate(selected, start=1):
            print()
            print(SUB_LINE)
            quiz.display(number)
            user_answer = self.inputs.read_int("정답 입력: ", 1, Quiz.CHOICE_COUNT)
            if quiz.is_correct(user_answer):
                correct_count += 1
                print("✅ 정답입니다!")
            else:
                print(f"❌ 오답입니다. 정답은 {quiz.correct_choice_text()} 입니다.")

        score = self.calculate_score(correct_count, total)
        is_new_best = self.update_best_score(score, correct_count, total)
        self.save_state()

        print()
        print(LINE)
        print(f"🏆 결과: {total}문제 중 {correct_count}문제 정답! ({score}점)")
        if is_new_best:
            print("🎉 새로운 최고 점수입니다!")
        print(LINE)

    def update_best_score(self, score: int, correct_count: int, total: int) -> bool:
        """최고 점수와 비교해 갱신한다. 갱신되면 True."""
        if self.best_score is not None and score <= self.best_score:
            return False
        self.best_score = score
        self.best_detail = {"correct": correct_count, "total": total}
        return True

    @staticmethod
    def calculate_score(correct_count: int, total: int) -> int:
        """100점 만점 기준 점수를 계산한다."""
        if total == 0:
            return 0
        return round(correct_count / total * 100)

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

    def show_score(self) -> None:
        """최고 점수를 보여준다."""
        if self.best_score is None:
            print("\n📭 아직 퀴즈를 풀지 않았습니다. 먼저 퀴즈를 풀어 보세요!")
            return

        detail = ""
        if self.best_detail:
            detail = (f" ({self.best_detail.get('total')}문제 중 "
                      f"{self.best_detail.get('correct')}문제 정답)")
        print(f"\n🏆 최고 점수: {self.best_score}점{detail}")

    def delete_quiz(self) -> None:
        print("\n🚧 준비 중인 기능입니다.")

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

        best = "없음" if self.best_score is None else f"{self.best_score}점"
        print(f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고점수 {best})")

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
        self.best_score = None
        self.best_detail = None
        self.history = []

    def to_state(self) -> dict:
        """저장할 데이터를 JSON 으로 바꿀 수 있는 dict 로 만든다."""
        return {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "best_detail": self.best_detail,
            "history": self.history,
        }

    def apply_state(self, data: dict) -> None:
        """불러온 dict 를 검증한 뒤 속성에 반영한다. 형식이 틀리면 ValueError."""
        raw_quizzes = data.get("quizzes")
        if not isinstance(raw_quizzes, list):
            raise ValueError("'quizzes' 항목이 목록이 아닙니다.")
        quizzes = [Quiz.from_dict(item) for item in raw_quizzes]

        best_score = data.get("best_score")
        if best_score is not None and (
            isinstance(best_score, bool) or not isinstance(best_score, int)
            or not 0 <= best_score <= 100
        ):
            raise ValueError("'best_score' 는 0~100 사이 정수 또는 null 이어야 합니다.")

        best_detail = data.get("best_detail")
        if best_detail is not None and not isinstance(best_detail, dict):
            raise ValueError("'best_detail' 형식이 올바르지 않습니다.")

        history = data.get("history", [])
        if not isinstance(history, list):
            raise ValueError("'history' 항목이 목록이 아닙니다.")

        # 모든 검증을 통과한 뒤에 한꺼번에 반영한다.
        self.quizzes = quizzes
        self.best_score = best_score
        self.best_detail = best_detail
        self.history = [record for record in history if isinstance(record, dict)]
