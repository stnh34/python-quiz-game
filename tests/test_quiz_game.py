"""표준 라이브러리 unittest 로 핵심 로직을 검증한다.

실행: python -m unittest discover -s tests -v
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from default_quizzes import create_default_quizzes  # noqa: E402
from game import QuizGame  # noqa: E402
from quiz import Quiz  # noqa: E402
from score_board import ScoreBoard  # noqa: E402


class QuizTest(unittest.TestCase):
    def test_default_quizzes_at_least_five(self):
        quizzes = create_default_quizzes()
        self.assertGreaterEqual(len(quizzes), 5)
        self.assertTrue(all(isinstance(q, Quiz) for q in quizzes))

    def test_is_correct(self):
        quiz = Quiz("Q", ["a", "b", "c", "d"], 2)
        self.assertTrue(quiz.is_correct(2))
        self.assertFalse(quiz.is_correct(1))

    def test_invalid_quiz_rejected(self):
        with self.assertRaises(ValueError):
            Quiz("Q", ["a", "b", "c"], 1)          # 선택지 3개
        with self.assertRaises(ValueError):
            Quiz("Q", ["a", "b", "c", "d"], 5)     # 정답 범위 밖
        with self.assertRaises(ValueError):
            Quiz.from_dict({"choices": ["a", "b", "c", "d"], "answer": 1})  # question 없음

    def test_dict_round_trip(self):
        quiz = Quiz("Q", ["a", "b", "c", "d"], 3, "힌트")
        self.assertEqual(Quiz.from_dict(quiz.to_dict()).to_dict(), quiz.to_dict())


class ScoreBoardTest(unittest.TestCase):
    def test_calculate_score_with_hint_penalty(self):
        self.assertEqual(ScoreBoard.calculate_score(4, 5), 80)
        self.assertEqual(ScoreBoard.calculate_score(2, 2, hints_used=1), 95)
        self.assertEqual(ScoreBoard.calculate_score(0, 3, hints_used=3), 0)  # 최소 0점

    def test_best_score_updates_only_when_higher(self):
        board = ScoreBoard()
        self.assertTrue(board.record_game(5, 3, 0, 60))
        self.assertFalse(board.record_game(5, 2, 0, 40))
        self.assertTrue(board.record_game(5, 5, 0, 100))
        self.assertEqual(board.best_score, 100)
        self.assertEqual(len(board.history), 3)


class StatePersistenceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "state.json"

    def tearDown(self):
        self.tmp.cleanup()

    def load_game(self) -> QuizGame:
        game = QuizGame(self.path)
        with redirect_stdout(io.StringIO()):
            game.load_state()
        return game

    def test_missing_file_uses_defaults_and_creates_file(self):
        game = self.load_game()
        self.assertEqual(len(game.quizzes), len(create_default_quizzes()))
        self.assertTrue(self.path.exists())

    def test_save_and_reload_keeps_quizzes_and_best_score(self):
        game = self.load_game()
        game.quizzes.append(Quiz("새 문제", ["a", "b", "c", "d"], 1))
        game.scores.record_game(5, 4, 0, 80)
        game.save_state()

        reloaded = self.load_game()
        self.assertEqual(reloaded.quizzes[-1].question, "새 문제")
        self.assertEqual(reloaded.scores.best_score, 80)

    def test_file_is_utf8_with_korean(self):
        self.load_game()
        text = self.path.read_text(encoding="utf-8")
        self.assertIn("자료형", text)
        self.assertIn("quizzes", json.loads(text))

    def test_corrupted_file_is_backed_up_and_restored(self):
        self.path.write_text("{broken json", encoding="utf-8")
        game = self.load_game()
        self.assertEqual(len(game.quizzes), len(create_default_quizzes()))
        self.assertTrue(self.path.with_name("state.json.bak").exists())
        json.loads(self.path.read_text(encoding="utf-8"))  # 복구된 파일은 정상 JSON


if __name__ == "__main__":
    unittest.main()
