from typing import override

from ..persistent import Persistent

PERSISTENT_FILE_PATH = "persistent.json"
USERS_LIST_FILE_PATH = "users_lists.json"


class AppData(Persistent):
    chat_id: int = 0
    admin_id: int = 0
    new_chat_id: int | None = None

    @override
    @classmethod
    def _file_name(cls) -> str:
        return PERSISTENT_FILE_PATH


__persistent: AppData | None = None


def app_data() -> AppData:
    global __persistent
    if __persistent:
        return __persistent
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
