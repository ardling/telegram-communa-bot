import json
from pathlib import Path
from pydantic import BaseModel

from .logging_setup import setup_logging
from .settings import get_data_path

logger = setup_logging(__file__)

PERSISTENT_FILE_PATH = "persistent.json"


class Persistent(BaseModel):
    chat_id: int = 0
    new_chat_id: int | None = None

    @staticmethod
    def load():
        path: Path = get_data_path().joinpath(PERSISTENT_FILE_PATH)

        logger.info("Load data from path {}", path)

        try:
            return Persistent.model_validate(
                json.loads(path.read_text(encoding="utf-8"))
            )
        except FileNotFoundError:
            data = Persistent()
            data.save()
            return data

    def save(self) -> None:
        path: Path = get_data_path().joinpath(PERSISTENT_FILE_PATH)

        logger.info("Save data from path {}", path)

        _ = path.write_text(self.model_dump_json(indent=2), encoding="utf-8")


__persistent: Persistent | None = None


def app_data() -> Persistent:
    global __persistent
    if not __persistent:
        __persistent = Persistent.load()
    return __persistent
