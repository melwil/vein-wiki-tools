from pydantic import Field

from vein_wiki_tools.clients.pakdump.models import UEBaseModel, UECultureInvariantString, UELocalizedString, UEModel, UEReference


class UEBulletInfoProperties(UEBaseModel):
    bullet_damage: float = Field(..., alias="BulletDamage")
    bullet_damage_type: UEReference = Field(..., alias="BulletDamageType")


class UEBulletType(UEModel):
    properties: UEBulletInfoProperties = Field(..., alias="Properties")


class UEEquippableItemAttachmentSlotProperties(UEBaseModel):
    label: UELocalizedString | UECultureInvariantString | None = Field(default=None, alias="Label")


class UEEquippableItemAttachmentSlot(UEModel):
    properties: UEEquippableItemAttachmentSlotProperties = Field(..., alias="Properties")


class UEBodySetup(UEModel):
    pass
