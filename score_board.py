"""점수 계산, 최고 점수, 게임 기록(history)을 관리하는 ScoreBoard 클래스."""

from datetime import datetime

HINT_PENALTY = 5           # 힌트 1회 사용 시 차감 점수
HISTORY_DISPLAY_COUNT = 5  # 점수 확인 화면에 보여줄 최근 기록 수
SUB_LINE = "-" * 40


class ScoreBoard:
    """best_score / best_detail / history 를 보관하고 갱신한다."""

    def __init__(self, best_score: int | None = None, best_detail: dict | None = None,
                 history: list[dict] | None = None):
        self.best_score = best_score      # 아직 풀지 않았으면 None
        self.best_detail = best_detail    # {"correct": 4, "total": 5}
        self.history = history or []      # 게임별 기록

    @staticmethod
    def calculate_score(correct_count: int, total: int, hints_used: int = 0) -> int:
        """100점 만점 기준 점수. 힌트 1회당 HINT_PENALTY 점 차감(최소 0점)."""
        if total == 0:
            return 0
        score = round(correct_count / total * 100) - hints_used * HINT_PENALTY
        return max(0, score)

    def has_played(self) -> bool:
        return self.best_score is not None

    def record_game(self, total: int, correct_count: int, hints_used: int, score: int) -> bool:
        """게임 결과를 기록하고 최고 점수를 갱신한다. 새 최고 점수면 True."""
        self.history.append({
            "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": total,
            "correct": correct_count,
            "hints_used": hints_used,
            "score": score,
        })
        if self.best_score is not None and score <= self.best_score:
            return False
        self.best_score = score
        self.best_detail = {"correct": correct_count, "total": total}
        return True

    def best_text(self) -> str:
        return "없음" if self.best_score is None else f"{self.best_score}점"

    def display(self) -> None:
        """최고 점수와 최근 기록을 출력한다."""
        if not self.has_played():
            print("\n📭 아직 퀴즈를 풀지 않았습니다. 먼저 퀴즈를 풀어 보세요!")
            return

        detail = ""
        if self.best_detail:
            detail = (f" ({self.best_detail.get('total')}문제 중 "
                      f"{self.best_detail.get('correct')}문제 정답)")
        print(f"\n🏆 최고 점수: {self.best_score}점{detail}")
        self.display_history()

    def display_history(self) -> None:
        """최근 게임 기록을 최신순으로 출력한다."""
        if not self.history:
            return
        recent = self.history[-HISTORY_DISPLAY_COUNT:][::-1]
        print(f"\n📜 최근 기록 (최근 {len(recent)}회 / 전체 {len(self.history)}회)")
        print(SUB_LINE)
        for record in recent:
            print(f"{record.get('played_at', '-')} | "
                  f"{record.get('total', '?')}문제 중 {record.get('correct', '?')}문제 정답 | "
                  f"힌트 {record.get('hints_used', 0)}회 | {record.get('score', '?')}점")
        print(SUB_LINE)

    def to_dict(self) -> dict:
        return {
            "best_score": self.best_score,
            "best_detail": self.best_detail,
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScoreBoard":
        """state.json 의 점수 관련 항목을 검증해 ScoreBoard 를 만든다. 틀리면 ValueError."""
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

        return cls(best_score, best_detail, [r for r in history if isinstance(r, dict)])
