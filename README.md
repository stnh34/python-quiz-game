# 🎯 나만의 퀴즈 게임

## 1. 프로젝트 개요

터미널에서 동작하는 **Python 콘솔 퀴즈 게임**입니다.
메뉴에서 번호를 골라 퀴즈를 풀고, 새 퀴즈를 등록하고, 목록과 최고 점수를 확인할 수 있습니다.
퀴즈와 점수는 프로젝트 루트의 `state.json`에 저장되므로 **프로그램을 껐다 켜도 데이터가 유지**됩니다.

- 표준 라이브러리만 사용 (`json`, `random`, `datetime`, `pathlib`, `os`, `sys`)
- 역할별 클래스 분리: `Quiz`, `QuizGame`, `ScoreBoard`, `StateStorage`, `InputHandler`
- Git 브랜치 작업 → 병합, 기능 단위 커밋으로 이력 관리

## 2. 퀴즈 주제와 선정 이유

**주제: Python 기초 문법**

이 프로젝트 자체가 Python 기초(자료형, 조건/반복문, 클래스, 파일 입출력, JSON)를 익히기 위한 과제입니다.
퀴즈를 만들면서 개념을 한 번 더 정리하고, 게임을 플레이하면서 다시 복습할 수 있도록
**"만드는 과정과 푸는 과정이 모두 학습이 되는"** 주제로 선택했습니다.
기본 퀴즈 7문제가 포함되어 있고, 각 문제에는 힌트가 있습니다.

## 3. 실행 방법

**요구 사항:** Python 3.10 이상 (외부 라이브러리 설치 불필요)

```bash
git clone https://github.com/stnh34/python-quiz-game.git
cd python-quiz-game
python main.py
```

> Windows 에서 `python` 명령이 없다면 `py main.py` 로 실행합니다.

## 4. 기능 목록

| 메뉴 | 기능 | 설명 |
|---|---|---|
| 1 | 퀴즈 풀기 | 풀 문제 수 선택 → 무작위 순서로 출제 → 정답/오답 안내 → 결과(점수) 표시, 최고 점수 갱신 |
| 2 | 퀴즈 추가 | 문제, 선택지 4개, 정답 번호(1-4), 힌트(선택)를 입력받아 등록 후 즉시 저장 |
| 3 | 퀴즈 목록 | 등록된 퀴즈를 번호와 함께 출력 |
| 4 | 점수 확인 | 최고 점수(정답 수 포함)와 최근 5회 게임 기록 표시 |
| 5 | 퀴즈 삭제 | 번호 선택 + y/n 확인 후 삭제, 파일에 반영 (0 입력 시 취소) |
| 6 | 종료 | 데이터 저장 후 종료 |

**보너스 기능:** 랜덤 출제, 문제 수 선택, 힌트(`h` 입력, 1회당 -5점), 퀴즈 삭제, 점수 기록 히스토리

**입력/예외 처리**
- 모든 입력은 앞뒤 공백을 제거한 뒤 처리합니다. (` 1 ` → `1`)
- 빈 입력, 숫자가 아닌 입력(`abc`), 범위 밖 숫자(메뉴 `9`, 정답 `0`)는 안내 후 다시 입력받습니다.
- `Ctrl+C`(KeyboardInterrupt) 또는 입력 스트림 종료(EOFError) 시 안내 메시지를 출력하고 저장 후 안전하게 종료합니다.
- 퀴즈가 없을 때 풀기/목록/삭제, 아직 풀지 않았을 때 점수 확인은 안내 메시지를 출력합니다.

**점수 계산:** `round(정답 수 / 문제 수 × 100) - 힌트 사용 횟수 × 5` (최소 0점)

## 5. 파일 구조

```
python-quiz-game/
├── main.py              # 실행 진입점: state.json 경로 지정, QuizGame 실행
├── game.py              # QuizGame: 메뉴 루프, 풀기/추가/목록/점수/삭제, 저장·불러오기 조율
├── quiz.py              # Quiz: 문제/선택지/정답/힌트, 출력·정답 확인·dict 변환
├── score_board.py       # ScoreBoard: 점수 계산, 최고 점수, 게임 기록(history)
├── storage.py           # StateStorage: state.json UTF-8 읽기/쓰기, 손상 파일 백업
├── input_handler.py     # InputHandler: 공통 입력 검증 (공백/빈 입력/숫자/범위/y·n)
├── default_quizzes.py   # 기본 퀴즈 7문제 (Quiz 인스턴스)
├── state.json           # 실행 시 자동 생성되는 데이터 파일 (Git 추적 제외)
├── .gitignore
└── README.md
```

## 6. 데이터 파일 설명 (`state.json`)

- **경로:** 프로젝트 루트 `./state.json` (`main.py` 와 같은 폴더, 실행 위치와 무관)
- **인코딩:** UTF-8 (`ensure_ascii=False` 로 한글을 그대로 저장)
- **역할:** 퀴즈 목록, 최고 점수, 게임 기록을 보관하여 재실행 시에도 데이터 유지
- **생성/저장 시점:** 첫 실행 시 기본 퀴즈로 생성 → 퀴즈 추가/삭제, 퀴즈 풀이 종료, 프로그램 종료(중단 포함) 시 저장
- **안전 저장:** `state.json.tmp` 에 먼저 쓴 뒤 교체하여 저장 도중 중단돼도 기존 파일이 깨지지 않음
- **예외 처리**
  - 파일 없음 → 기본 퀴즈 데이터로 시작
  - JSON 형식 오류 / 필드 형식 오류 → 안내 메시지 출력, 기존 파일을 `state.json.bak` 으로 보관한 뒤 기본 데이터로 복구
  - 쓰기 실패 → 안내 메시지 출력 후 게임은 계속 진행

**스키마**

| 키 | 타입 | 설명 |
|---|---|---|
| `quizzes` | list | 퀴즈 목록 |
| `quizzes[].question` | str | 문제 |
| `quizzes[].choices` | list[str] | 선택지 4개 |
| `quizzes[].answer` | int | 정답 번호 (1~4) |
| `quizzes[].hint` | str | 힌트 (없으면 빈 문자열, 생략 가능) |
| `best_score` | int \| null | 최고 점수 (0~100), 아직 풀지 않았으면 `null` |
| `best_detail` | object \| null | 최고 점수 당시 `{"correct": 정답 수, "total": 문제 수}` |
| `history` | list | 게임 기록 `{"played_at", "total", "correct", "hints_used", "score"}` |

**예시**

```json
{
    "quizzes": [
        {
            "question": "Python에서 변경할 수 없는(immutable) 자료형은?",
            "choices": ["list", "dict", "tuple", "set"],
            "answer": 3,
            "hint": "소괄호 ( ) 로 만드는 자료형입니다."
        }
    ],
    "best_score": 80,
    "best_detail": {"correct": 4, "total": 5},
    "history": [
        {"played_at": "2026-11-20 00:30:00", "total": 5, "correct": 4, "hints_used": 0, "score": 80}
    ]
}
```

## 7. 실행 화면 예시

```
========================================
        🎯 나만의 퀴즈 게임 🎯
========================================
📂 저장된 데이터를 불러왔습니다. (퀴즈 7개, 최고점수 80점)

========================================
1. 퀴즈 풀기
2. 퀴즈 추가
3. 퀴즈 목록
4. 점수 확인
5. 퀴즈 삭제
6. 종료
========================================
선택: abc
⚠️ 잘못된 입력입니다. 1-6 사이의 숫자를 입력하세요.
```

스크린샷: `docs/screenshots/` (menu.png, play.png, add_quiz.png, score.png)

## 8. Git 작업 흐름

- 기능 단위 커밋: `Feat:` / `Refactor:` / `Docs:` / `Chore:` 접두어로 변경 요약
- `feature/play-quiz` 브랜치에서 퀴즈 풀기 기능 개발 후 `main` 으로 `--no-ff` 병합
- 별도 디렉터리에 `clone` → 수정/커밋/푸시 → 원래 작업 디렉터리에서 `pull` 로 반영 확인

```bash
git log --oneline --graph
```
