from pydantic import Field

from vein_wiki_tools.clients.pakdump.models import UEBaseModel, UECultureInvariantString, UELocalizedString, UEModel, UEReference


class UEToolProperties(UEBaseModel):
    name: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="Name")
    improper_name: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="ImproperName")
    parents: list[UEReference] | None = Field(default=None, alias="Parents")


class UETool(UEModel):
    properties: UEToolProperties = Field(..., alias="Properties")
