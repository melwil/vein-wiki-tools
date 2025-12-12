from pydantic import Field

from vein_wiki_tools.clients.pakdump.models import UEBaseModel, UEModel, UEReference


class UEBulletInfoProperties(UEBaseModel):
    bullet_damage: float = Field(..., alias="BulletDamage")
    bullet_damage_type: UEReference = Field(..., alias="BulletDamageType")


class UEBulletType(UEModel):
    properties: UEBulletInfoProperties = Field(..., alias="Properties")
