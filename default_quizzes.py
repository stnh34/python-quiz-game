"""기본 퀴즈 데이터 (주제: Python 기초 문법).

state.json 이 없거나 손상되었을 때 이 데이터로 시작/복구한다.
"""

from quiz import Quiz


def create_default_quizzes() -> list[Quiz]:
    """기본 퀴즈를 Quiz 인스턴스 목록으로 새로 만들어 반환한다."""
    return [
        Quiz(
            "Python에서 변경할 수 없는(immutable) 자료형은?",
            ["list", "dict", "tuple", "set"],
            3,
            "소괄호 ( ) 로 만드는 자료형입니다.",
        ),
        Quiz(
            "print(type(3 / 2)) 의 출력 결과는?",
            ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'bool'>"],
            2,
            "Python 3 에서 / 연산은 항상 소수점 결과를 냅니다.",
        ),
        Quiz(
            "클래스의 메서드에서 객체 자신을 가리키는 첫 번째 매개변수 이름(관례)은?",
            ["this", "me", "self", "cls"],
            3,
            "__init__(self, ...) 에서도 볼 수 있습니다.",
        ),
        Quiz(
            "반복 횟수가 정해져 있지 않고, 조건이 참인 동안 반복할 때 적합한 문은?",
            ["for", "while", "if", "def"],
            2,
            "'~하는 동안'이라는 뜻의 영어 단어입니다.",
        ),
        Quiz(
            "dict 에서 키가 없을 때 KeyError 대신 기본값을 돌려주는 메서드는?",
            ["get()", "pop()", "keys()", "find()"],
            1,
            "d.___('키', 기본값) 형태로 사용합니다.",
        ),
        Quiz(
            "파일을 다룰 때 사용이 끝나면 자동으로 close() 해 주는 문법은?",
            ["try", "with", "lambda", "yield"],
            2,
            "with open(...) as f: 형태로 씁니다.",
        ),
        Quiz(
            "JSON 문자열을 Python 객체(dict 등)로 바꾸는 함수는?",
            ["json.dumps()", "json.dump()", "json.loads()", "json.parse()"],
            3,
            "'load string' 의 줄임말입니다.",
        ),
    ]
