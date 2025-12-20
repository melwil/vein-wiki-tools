import re

from pydantic import Field

from vein_wiki_tools.clients.pakdump.models import UEBaseModel, UECultureInvariantString, UELocalizedString, UEModel, UEModelInfo, UEQuantityModel, UEReference, UEStrKeyFloatValuePair


class UEBuildObjectProperties(UEBaseModel):
    name: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="Name")
    description: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="Description")
    build_requirements: list[UEQuantityModel] = Field(default_factory=list, alias="BuildRequirements")
    tool_object_requirements: list[UEReference] = Field(default_factory=list, alias="ToolObjectRequirements")
    stat_requirements: list[UEStrKeyFloatValuePair] = Field(default_factory=list, alias="StatRequirements")
    maintenance_cost: list[UEQuantityModel] = Field(default_factory=list, alias="MaintenanceCost")
    result_xp: list[UEStrKeyFloatValuePair] = Field(default_factory=list, alias="XPOnBuild")
    build_object_category: UEReference | None = Field(default=None, alias="BuildObjectCategory")
    resulting_actor: UEReference | None = Field(default=None, alias="ResultingActor")


class UEBuildObject(UEModel):
    properties: UEBuildObjectProperties = Field(..., alias="Properties")
    _model_info: UEModelInfo = UEModelInfo()

    @property
    def model_info(self) -> UEModelInfo:
        if boc := self.get_prop("build_object_category"):
            if match := re.match(r"BuildObjectCategory'BOC_(\w+)'", boc.object_name):
                self._model_info.super_type = "buildable object"
                self._model_info.sub_type = match.group(1).lower()
                self._model_info.template = "item"
        return self._model_info


class UEBuildObjectCategoryProperties(UEBaseModel):
    label: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="Label")


class UEBuildObjectCategory(UEModel):
    properties: UEBuildObjectCategoryProperties = Field(..., alias="Properties")


class UEDoorWhitelist(UEModel):
    pass


class UEFenceWhitelist(UEModel):
    pass
