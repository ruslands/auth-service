import enum
from typing import Literal, Optional

from core.constants import EMPTY_VALUE


class EnumMixin(enum.Enum):
    @classmethod
    def get_info(cls, include_empty=True):
        base = {row.name: row.value for row in cls}
        if include_empty:
            base.update({EMPTY_VALUE: EMPTY_VALUE})
        return base

    @classmethod
    def keys_annotation(cls, optional=True):
        """В схемах много строк вида:
        Optional[Literal[*SomeEnum.get_keys()] | list[Literal[*SomeEnum.get_keys()] | None]]

        Можно заменить их на Optional[SomeEnum.keys_annotation()]
        Или дописать кастомный тип со сходной логикой.
        """

        keys = cls.get_keys()
        single_annotation = Literal[*keys]
        annotation = single_annotation | list[single_annotation | None]
        return Optional[annotation] if optional else annotation

    @classmethod
    def get_keys(cls) -> list[str]:
        return [x.name for x in cls]

    @classmethod
    def get_value_for_key(cls, name):
        for x in cls:
            if x.name == name:
                return x.value
        return None

    @classmethod
    def get_key_for_value(cls, value):
        for x in cls:
            if x.value == value:
                return x.name
        return None

    @classmethod
    def get_list(cls):
        return [x.value for x in cls]
