from enum import Enum
from typing import TypeAlias

from pydantic import BaseModel, Field, conint, conlist, validator
from pydantic.color import Color

from dnd.database.schemas.pawns import PawnTypeEnum
from dnd.models.auth import UserInfoModel

XYType: TypeAlias = conlist(conint(ge=1), min_items=2, max_items=2)


class MovablePawnSizeEnum(Enum):
    small: XYType = (2, 2)
    medium: XYType = (5, 5)
    large: XYType = (10, 10)
    huge: XYType = (15, 15)
    gigantic: XYType = (20, 20)

    @classmethod
    def get_all_sizes(cls):
        return (
            cls.small,
            cls.medium,
            cls.large,
            cls.huge,
            cls.gigantic,
        )


class PawnMetaModel(BaseModel):
    visibility: bool
    type: PawnTypeEnum
    size_x: int
    size_y: int
    x: int | None
    y: int | None
    color: Color

    class Config:
        orm_mode = True


class PawnModel(BaseModel):
    name: str
    user: UserInfoModel
    meta: PawnMetaModel

    class Config:
        orm_mode = True


class PawnMetaRequestModel(BaseModel):
    position: XYType | tuple[None, None] = (
        None,
        None,
    )
    type: PawnTypeEnum = PawnTypeEnum.movable
    color: Color = Field(example=Color("white"))
    size: XYType

    @classmethod
    @validator("size")
    def size_validator(cls, val: XYType, values: dict):
        if (
            val is not None
            and values.get("type") is PawnTypeEnum.movable
            and val not in MovablePawnSizeEnum.get_all_sizes()
        ):
            raise ValueError("Not available size for movable type")


class UpdatePawnMetaRequestModel(PawnMetaRequestModel):
    position: XYType | conlist(None, min_items=2, max_items=2) | None = (
        None,
        None,
    )
    type: PawnTypeEnum | None
    color: Color | None = Field(example=Color("white"))
    size: XYType | None


class PawnMoveModel(BaseModel):
    new_position: XYType | conlist(None, min_items=2, max_items=2) = (
        None,
        None,
    )
