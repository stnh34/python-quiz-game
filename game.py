"""게임 전체 흐름을 관리하는 QuizGame 클래스."""

import random

from default_quizzes import create_default_quizzes
from input_handler import InputHandler
from quiz import Quiz

LINE = "=" * 40
SUB_LINE = "-" * 40


class QuizGame:
    """메뉴 표시와 각 기능 실행을 담당한다."""

    MENU_ITEMS = ("퀴즈 풀기", "퀴즈 추가", "퀴즈 목록", "점수 확인", "퀴즈 삭제", "종료")

    def __init__(self):
        self.inputs = InputHandler()
        self.quizzes: list[Quiz] = create_default_quizzes()

    # ------------------------------------------------------------------
    # 메인 루프
    # ------------------------------------------------------------------
    def run(self) -> None:
        """프로그램 진입점. Ctrl+C / 입력 종료(EOF)에도 안전하게 끝낸다."""
        self.print_title()
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
        print()
        print(LINE)
        print(f"🏆 결과: {total}문제 중 {correct_count}문제 정답! ({score}점)")
        print(LINE)

    @staticmethod
    def calculate_score(correct_count: int, total: int) -> int:
        """100점 만점 기준 점수를 계산한다."""
        if total == 0:
            return 0
        return round(correct_count / total * 100)

    def add_quiz(self) -> None:
        print("\n🚧 준비 중인 기능입니다.")

    def list_quizzes(self) -> None:
        print("\n🚧 준비 중인 기능입니다.")

    def show_score(self) -> None:
        print("\n🚧 준비 중인 기능입니다.")

    def delete_quiz(self) -> None:
        print("\n🚧 준비 중인 기능입니다.")

    def exit_game(self) -> None:
        print("\n👋 게임을 종료합니다. 다음에 또 만나요!")

    def on_interrupt(self) -> None:
        """중단 시 정리 작업 (저장 기능 구현 후 확장)."""
