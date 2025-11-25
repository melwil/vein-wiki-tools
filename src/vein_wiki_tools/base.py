from pydantic import BaseModel, ConfigDict


class RootSchema(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        use_enum_values=True,
        validate_by_name=True,
        validate_by_alias=True,
    )
