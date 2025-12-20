from typing import Type

from vein_wiki_tools.clients.pakdump.build import *  # noqa
from vein_wiki_tools.clients.pakdump.firearms import *  # noqa
from vein_wiki_tools.clients.pakdump.models import UEModel
from vein_wiki_tools.clients.pakdump.recipes import *  # noqa


def get_subclass_type(type_name: str | None) -> Type[UEModel] | None:
    if type_name is None:
        return None
    type_name = type_name.lower()
    if not type_name.startswith("ue"):
        type_name = "ue" + type_name

    for subclass in UEModel.get_subclasses():
        if subclass.__name__.lower() == type_name:
            return subclass

    return None
