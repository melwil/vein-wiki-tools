from pydantic import Field

from vein_wiki_tools.clients.pakdump.models import UEBaseModel, UECultureInvariantString, UELocalizedString, UEModel, UEModelInfo, UEQuantityModel, UEReference, UEStrKeyFloatValuePair


class UEPossibleIngredients(UEBaseModel):
    ingredients: list[UEQuantityModel] = Field(default_factory=list, alias="Ingredients")
    tool_objects: list[UEReference] | None = Field(default=None, alias="ToolObjects")
    fluids: list[UEStrKeyFloatValuePair] | None = Field(default=None, alias="Fluids")
    only_one_ingredient_required: bool | None = Field(default=None, alias="bOnlyOneIngredientRequired")
    workbench_type: UEReference | None = Field(default=None, alias="WorkbenchType")
    enabled: bool | None = Field(default=None, alias="bEnabled")


class UEBaseRecipeProperties(UEBaseModel):
    recipe_name: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="RecipeName")
    recipe_flavor_text: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="RecipeFlavorText")
    craft_time: float | None = Field(default=None, alias="CraftTime")
    results: list[UEQuantityModel] = Field(default_factory=list, alias="Results")
    recipe_type: UEReference | None = Field(default=None, alias="RecipeType")
    possible_ingredients: list[UEPossibleIngredients] = Field(..., alias="PossibleIngredients")
    heat_converter_types: list[UEReference] | None = Field(default=None, alias="HeatConverterTypes")
    # Overcooking
    cook_limit: float | None = Field(default=None, alias="CookLimit")
    cook_limit_override: UEReference | None = Field(default=None, alias="CookLimitOverride")
    # XP
    cooking_reward_xp: list[UEStrKeyFloatValuePair] = Field(default_factory=list, alias="CookingRewardXP")
    crafting_reward_xp: list[UEStrKeyFloatValuePair] = Field(default_factory=list, alias="CraftingRewardXP")
    result_xp: list[UEStrKeyFloatValuePair] = Field(default_factory=list, alias="ResultXP")


class UEBaseRecipe(UEModel):
    properties: UEBaseRecipeProperties = Field(..., alias="Properties")
    _model_info: UEModelInfo = UEModelInfo(sub_type="base_recipe", super_type="recipe")


class UEHeatConverterRecipe(UEModel):
    properties: UEBaseRecipeProperties = Field(..., alias="Properties")
    _model_info: UEModelInfo = UEModelInfo(sub_type="heat_converter_recipe", super_type="recipe")
