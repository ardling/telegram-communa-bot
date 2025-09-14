import json
from pathlib import Path
from pydantic import BaseModel

from .logging_setup import setup_logging
from .settings import settings

logger = setup_logging(__file__)


class Persistent(BaseModel):
    @classmethod
    def _file_name(cls) -> str:
        raise NotImplemented

    @classmethod
    def file_path(cls) -> Path:
        return settings().data_path.joinpath(cls._file_name())

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
