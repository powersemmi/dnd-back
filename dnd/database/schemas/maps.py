from typing import TYPE_CHECKING, Optional, Self

from sqlalchemy import ForeignKey, UniqueConstraint, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dnd.database.schemas.base import BaseSchema

if TYPE_CHECKING:
    from dnd.database.schemas.users import User


class Map(BaseSchema):
    __tablename__ = "maps"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str]

    user: Mapped["User"] = relationship(back_populates="maps", lazy="joined")

    meta: Mapped["MapMeta"] = relationship(
        back_populates="map", lazy="joined", cascade="all, delete"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="_user_id_map_uc"),
    )

    @classmethod
    async def get_by_name_and_user_id(
        cls, session: AsyncSession, name: str, user_id: int
    ) -> Self | None:
        return (
            await session.execute(
                select(cls).filter(
                    (cls.name == name), (cls.user_id == user_id)
                )
            )
        ).scalar_one_or_none()

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        user_id: int,
        name: str,
    ) -> Self:
        return await cls._create(
            session=session,
            user_id=user_id,
            name=name,
        )

    @classmethod
    async def update(cls, session: AsyncSession, id: int, name: str):
        return await cls._update(
            session=session, condition=(cls.id == id), name=name
        )


class MapMeta(BaseSchema):
    __tablename__ = "maps_meta"
    map_id = mapped_column(ForeignKey("maps.id"))
    len_x: Mapped[int]
    len_y: Mapped[int]
    image_short_url: Mapped[Optional[str]]

    map: Mapped["Map"] = relationship(back_populates="meta", lazy="joined")

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        map_id: int,
        len_x: int,
        len_y: int,
        image_short_url: Optional[str] = None,
    ) -> Self:
        return await cls._create(
            map_id=map_id,
            len_x=len_x,
            len_y=len_y,
            image_short_url=image_short_url,
            session=session,
        )

    @classmethod
    async def update(
        cls, session: AsyncSession, id: int, len_x: int, len_y, image_short_url
    ):
        return await cls._update(
            session=session,
            condition=(cls.id == id),
            len_x=len_x,
            len_y=len_y,
            image_short_url=image_short_url,
        )
