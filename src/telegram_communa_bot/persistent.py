import json
from pathlib import Path
from typing import override
from pydantic import BaseModel

from .logging_setup import setup_logging
from .settings import get_data_path

logger = setup_logging(__file__)

PERSISTENT_FILE_PATH = "persistent.json"
USERS_LIST_FILE_PATH = "users_lists.json"


class Persistent(BaseModel):
    @classmethod
    def _file_name(cls) -> str:
        raise NotImplemented

    @classmethod
    def file_path(cls) -> Path:
        return get_data_path().joinpath(cls._file_name())

    @classmethod
    def load(cls):
        path: Path = cls.file_path()

        logger.info("Load data from path %s", path)
        try:
            return cls.model_validate(json.loads(path.read_text(encoding="utf-8")))
        except FileNotFoundError:
            data = cls()
            data.save()
            return data

    def save(self) -> None:
        path: Path = self.file_path()
        logger.info("Save %s to %s", type(self), path)

        _ = path.write_text(self.model_dump_json(indent=2), encoding="utf-8")


class AppData(Persistent):
    chat_id: int = 0
    new_chat_id: int | None = None

    @override
    @classmethod
    def _file_name(cls) -> str:
        return PERSISTENT_FILE_PATH


__persistent: AppData | None = None


def app_data() -> AppData:
    global __persistent
    if not __persistent:
        __persistent = AppData.load()
    return __persistent


class UsersLists(Persistent):
    white_list: set[int] = set()
    black_list: set[int] = set()
    wait_list: set[int] = set()

    @override
    @classmethod
    def _file_name(cls) -> str:
        return USERS_LIST_FILE_PATH


__user_lists: UsersLists | None = None


def users_lists() -> UsersLists:
    global __user_lists
    if not __user_lists:
        __user_lists = UsersLists.load()
    return __user_lists
