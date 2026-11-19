"""state.json 파일 읽기/쓰기를 담당하는 StateStorage 클래스."""

import json
import os
from pathlib import Path


class StateCorruptedError(Exception):
    """state.json 내용이 JSON 형식이 아니거나 읽을 수 없을 때 발생한다."""


class StateStorage:
    """JSON 파일(UTF-8)에 게임 상태(dict)를 저장하고 불러온다."""

    ENCODING = "utf-8"

    def __init__(self, path: Path):
        self.path = Path(path)

    def exists(self) -> bool:
        return self.path.is_file()

    def load(self) -> dict | None:
        """파일을 읽어 dict 로 반환한다.

        - 파일이 없으면 None (첫 실행)
        - JSON 형식 오류/읽기 오류/최상위가 dict 가 아니면 StateCorruptedError
        """
        if not self.exists():
            return None
        try:
            with open(self.path, "r", encoding=self.ENCODING) as file:
                data = json.load(file)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise StateCorruptedError(f"JSON 형식이 올바르지 않습니다: {error}") from error
        except OSError as error:
            raise StateCorruptedError(f"파일을 읽을 수 없습니다: {error}") from error

        if not isinstance(data, dict):
            raise StateCorruptedError("최상위 데이터가 객체({})가 아닙니다.")
        return data

    def save(self, data: dict) -> None:
        """dict 를 JSON 으로 저장한다. 실패하면 OSError 를 그대로 전달한다.

        임시 파일에 먼저 쓴 뒤 교체하여, 저장 도중 중단돼도 기존 파일이 깨지지 않게 한다.
        """
        temp_path = self.path.with_name(self.path.name + ".tmp")
        with open(temp_path, "w", encoding=self.ENCODING) as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        os.replace(temp_path, self.path)

    def backup_corrupted(self) -> Path | None:
        """손상된 파일을 state.json.bak 으로 옮겨 보관한다."""
        if not self.exists():
            return None
        backup_path = self.path.with_name(self.path.name + ".bak")
        try:
            os.replace(self.path, backup_path)
        except OSError:
            return None
        return backup_path
