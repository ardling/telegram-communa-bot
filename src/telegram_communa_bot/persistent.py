from .logging_setup import setup_logging

logger = setup_logging(__file__)

import json
from typing import TypeVar, cast
from pathlib import Path
from pydantic import BaseModel

from .settings import settings

T = TypeVar("T", bound="Persistent")


class Persistent(BaseModel):
    @classmethod
    def _file_name(cls) -> str:
        raise NotImplemented

    @classmethod
    def file_path(cls) -> Path:
        return settings().data_path.joinpath(cls._file_name())

    @classmethod
    def get(cls: type[T]) -> T:
        return cast(T, _signltones[cls.__name__])

    @classmethod
    def load(cls: type[T]) -> T:
        path: Path = cls.file_path()

        logger.info("Load data from path %s", path)
        try:
            data = cls.model_validate(json.loads(path.read_text(encoding="utf-8")))

        except FileNotFoundError:
            data = cls()
            data.save()

        _signltones[cls.__name__] = data
        return data

    def save(self) -> None:
        path: Path = self.file_path()
        logger.info("Save %s to %s", type(self), path)

        _ = path.write_text(self.model_dump_json(indent=2), encoding="utf-8")


_signltones: dict[str, Persistent] = {}
