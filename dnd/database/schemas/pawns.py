from enum import Enum
from typing import TYPE_CHECKING, Self

from colour import Color
from sqlalchemy import ForeignKey, UniqueConstraint, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import ColorType

from dnd.database.schemas.base import BaseSchema

if TYPE_CHECKING:
    from dnd.database.schemas.game_sets import GameSet
    from dnd.database.schemas.users import User


class PawnTypeEnum(Enum):
    movable = "movable"
    static = "static"


class Pawn(BaseSchema):
    __tablename__ = "pawns"
    user_id = mapped_column(ForeignKey("users.id"))
    game_set_id = mapped_column(ForeignKey("game_sets.id"))
    name: Mapped[str]

    game_set: Mapped["GameSet"] = relationship(
        back_populates="pawns", lazy="joined"
    )
    user: Mapped["User"] = relationship(back_populates="pawns", lazy="joined")
    meta: Mapped["PawnMeta"] = relationship(
        back_populates="pawn", lazy="joined", cascade="all, delete"
    )

    __table_args__ = (
        UniqueConstraint("game_set_id", "name", name="_game_set_id_pawn_uc"),
    )

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        name: str,
        game_set_id: int,
        user_id: int,
    ) -> Self:
        return await cls._create(
            game_set_id=game_set_id,
            name=name,
            user_id=user_id,
            session=session,
        )

    @classmethod
    async def get_by_name_and_game_set_id(
        cls, session: AsyncSession, name: str, game_set_id: int
    ) -> Self | None:
        return (
            await session.execute(
                select(cls).where(
                    (cls.name == name), (cls.game_set_id == game_set_id)
                )
            )
        ).scalar_one_or_none()

    @classmethod
    async def update(cls, session: AsyncSession, id: int, name: str):
        return await cls._update(
            session=session,
            condition=(cls.id == id),
            name=name,
        )


class PawnMeta(BaseSchema):
    __tablename__ = "pawns_meta"
    visibility: Mapped[bool]
    type: Mapped[PawnTypeEnum]
    size_x: Mapped[int]
    size_y: Mapped[int]
    x: Mapped[int] = mapped_column(nullable=True)
    y: Mapped[int] = mapped_column(nullable=True)
    _color = mapped_column("color", ColorType, nullable=False)

    @hybrid_property
    def color(self) -> str:
        if isinstance(self._color, Color):
            return self._color.get_hex()
        return str(self._color)

    pawn_id = mapped_column(ForeignKey("pawns.id"))

    pawn: Mapped["Pawn"] = relationship(back_populates="meta", lazy="joined")

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        pawn_id: int,
        visibility: bool,
        color: hex,
        type: PawnTypeEnum = PawnTypeEnum.movable,
        position: tuple[int, int] | tuple[None, None] = (None, None),
        size: tuple[int, int] = (2, 2),
    ) -> Self:
        return await cls._create(
            pawn_id=pawn_id,
            visibility=visibility,
            type=type,
            x=position[0],
            y=position[1],
            size_x=size[0],
            size_y=size[1],
            _color=color,
            session=session,
        )

    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        id: int,
        visibility: bool,
        color: hex,
        type: PawnTypeEnum = PawnTypeEnum.movable,
        position: tuple[int, int] | tuple[None, None] = (None, None),
        size: tuple[int, int] = (2, 2),
    ):
        return await cls._update(
            session=session,
            condition=(cls.id == id),
            visibility=visibility,
            position=position,
            color=color,
            type=type,
            size=size,
        )
