from pydantic import Field

from vein_wiki_tools.clients.pakdump.models import (
    UEBaseModel,
    UECultureInvariantString,
    UELocalizedString,
    UEModel,
    UEModelInfo,
    UEReference,
    UEStrKeyFloatValuePair,
)


class UEFluidDefinitionProperties(UEBaseModel):
    name: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="Name")
    smell_text: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="SmellText")
    smell_rotten_text: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="SmellRottenText")
    decays: bool = Field(default=False, alias="bDecays")
    freezing_point_f: float | None = Field(default=None, alias="FreezingPoint")
    thirst_satisfaction_per_ml: float | None = Field(default=None, alias="ThirstSatisfactionPerMilliliter")
    sanitizes_wounds: bool = Field(default=False, alias="bSanitizesWounds")
    conditions_on_drink: UEReference | None = Field(default=None, alias="ConditionsOnDrink")
    conditions_on_inject: UEReference | None = Field(default=None, alias="ConditionsOnInject")
    density: float | None = Field(default=None, alias="Density")
    scent_strength: float | None = Field(default=None, alias="ScentStrength")
    scent_radius: float | None = Field(default=None, alias="ScentRadius")
    scent_radius_sqr: float | None = Field(default=None, alias="ScentRadiusSqr")
    detergent_multiplier: float | None = Field(default=None, alias="DetergentMultiplier")
    is_water: bool = Field(default=False, alias="bIsWater")
    fertilizer_effectiveness: float | None = Field(default=None, alias="FertilizerEffectiveness")


class UEFluidDefinition(UEModel):
    properties: UEFluidDefinitionProperties = Field(..., alias="Properties")
    _model_info: UEModelInfo = UEModelInfo(super_type="fluid", template="item")


class UEFoodConditionSetProperties(UEBaseModel):
    conditions_on_eat: list[UEStrKeyFloatValuePair] | None = Field(default=None, alias="ConditionsOnEat")
    addiction_types_on_eat: list[UEStrKeyFloatValuePair] | None = Field(default=None, alias="AddictionTypesOnEat")
    xp_gain: list[UEStrKeyFloatValuePair] | None = Field(default=None, alias="XPGain")
    auto_morphs: list[UEStrKeyFloatValuePair] | None = Field(default=None, alias="AutoMorphs")
    blood_sugar_impact: float | None = Field(default=None, alias="BloodSugarImpact")


class UEFoodConditionSet(UEModel):
    properties: UEFoodConditionSetProperties = Field(..., alias="Properties")
    _model_info: UEModelInfo = UEModelInfo(super_type="food_condition_set")
