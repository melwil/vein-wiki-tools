from typing import Type

from .common import NodeContent
from .items import *  # noqa


def get_subclass_type(type_name: str | None) -> Type[NodeContent] | None:
    if type_name is None:
        return None

    for subclass in NodeContent.get_subclasses():
        if subclass.__name__.lower() == type_name.lower():
            return subclass

    return None
