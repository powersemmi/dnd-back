from typing import TYPE_CHECKING, Optional, Self

from sqlalchemy import ForeignKey, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dnd.database.schemas.base import BaseSchema

if TYPE_CHECKING:
    from dnd.database.schemas.maps import Map
    from dnd.database.schemas.pawns import Pawn
    from dnd.database.schemas.users import User, UserInGameset


class GameSet(BaseSchema):
    __tablename__ = "game_sets"
    name: Mapped[str]
    short_url: Mapped[str] = mapped_column(unique=True, index=True)
    owner_id = mapped_column(ForeignKey("users.id"))

    owner: Mapped["User"] = relationship(
        back_populates="game_sets", lazy="joined"
    )

    meta: Mapped["GameSetMeta"] = relationship(
        back_populates="game_set", lazy="joined", cascade="all, delete"
    )
    pawns: Mapped[list["Pawn"]] = relationship(
        back_populates="game_set", lazy="selectin", cascade="all, delete"
    )

    users_in_game: Mapped[list["UserInGameset"]] = relationship(
        back_populates="game_set", lazy="selectin"
    )

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        name: str,
        short_url: str,
        owner_id: int,
        game_set_id: int,
    ):
        return await cls._create(
            id=game_set_id,
            owner_id=owner_id,
            name=name,
            short_url=short_url,
            session=session,
            users_in_game=[],
            pawns=[],
        )

    @classmethod
    async def update(cls, session: AsyncSession, id: int, name: str):
        return await cls._update(
            session=session, condition=(cls.id == id), name=name
        )

    @classmethod
    async def get_by_short_url(
        cls, session: AsyncSession, short_url: str
    ) -> Self | None:
        res = await session.execute(
            select(cls).filter(cls.short_url == short_url)
        )
        return res.scalar_one_or_none()

    @classmethod
    async def get_next_id(cls, session: AsyncSession) -> int:
        res = await session.execute(
            text("SELECT nextval('game_sets_id_seq');")
        )
        return res.fetchone()[0]


class GameSetMeta(BaseSchema):
    __tablename__ = "game_sets_meta"

    game_set_id = mapped_column(ForeignKey("game_sets.id"))
    map_id = mapped_column(ForeignKey("maps.id"), nullable=True)

    game_set: Mapped["GameSet"] = relationship(back_populates="meta")
    map: Mapped[Optional["Map"]] = relationship(lazy="joined")

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        game_set_id: GameSet.id,
        map_id: int | None = None,
    ) -> Self:
        return await cls._create(
            game_set_id=game_set_id,
            session=session,
            map_id=map_id,
        )

    @classmethod
    async def update(cls, session: AsyncSession, id: int, map_id: int | None):
        return await cls._update(
            session=session, condition=(cls.id == id), map_id=map_id
        )
