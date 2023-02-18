from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import constr
from sqlalchemy.ext.asyncio import AsyncSession

from dnd.database.db import get_db
from dnd.database.schemas.game_sets import GameSet
from dnd.database.schemas.maps import MapMeta
from dnd.database.schemas.pawns import Pawn, PawnMeta
from dnd.database.schemas.users import User
from dnd.models.pawn import (
    PawnMetaRequestModel,
    PawnModel,
    PawnMoveModel,
    UpdatePawnMetaRequestModel,
)
from dnd.procedures.auth import check_user
from dnd.procedures.game_set import get_current_game_set

router = APIRouter(prefix="/pawn", tags=["pawn"])


@router.get(
    "/{game_set_short_url}/{pawn_name}",
    response_model=PawnModel,
    status_code=200,
)
async def get_pawn(
    pawn_name: constr(max_length=30),
    game_set: GameSet = Depends(get_current_game_set),
    _: User = Depends(check_user),
    session: AsyncSession = Depends(get_db),
):
    pawn = await Pawn.get_by_name_and_game_set_id(
        session=session, game_set_id=game_set.id, name=pawn_name
    )
    if not pawn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.put(
    "/{game_set_short_url}/{pawn_name}",
    response_model=PawnModel,
    status_code=201,
)
async def create_pawn(
    pawn_name: constr(max_length=30),
    pawn_meta: PawnMetaRequestModel,
    game_set: GameSet = Depends(get_current_game_set),
    user: User = Depends(check_user),
    session: AsyncSession = Depends(get_db),
):
    visibility = False if user.id == game_set.owner.id else True
    exist_pawn = await Pawn.get_by_name_and_game_set_id(
        session=session, game_set_id=game_set.id, name=pawn_name
    )
    if exist_pawn:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    new_pawn = await Pawn.create(
        session=session,
        game_set_id=game_set.id,
        user_id=user.id,
        name=pawn_name,
    )
    new_pawn_meta = await PawnMeta.create(
        session=session,
        pawn_id=new_pawn.id,
        type=pawn_meta.type,
        visibility=visibility,
        position=pawn_meta.position,
        color=pawn_meta.color.as_hex(),
    )
    new_pawn.meta = new_pawn_meta
    new_pawn.user = user
    await session.commit()
    return PawnModel.from_orm(new_pawn)


@router.patch(
    "/{game_set_short_url}/{pawn_name}",
    response_model=PawnModel,
)
async def update_pawn(
    pawn_name: constr(max_length=30),
    pawn_meta: UpdatePawnMetaRequestModel,
    pawn_new_name: str | None = Query(max_length=30),
    game_set: GameSet = Depends(get_current_game_set),
    user: User = Depends(check_user),
    session: AsyncSession = Depends(get_db),
) -> PawnModel:
    if pawn_new_name:
        exist_pawn = await Pawn.get_by_name_and_game_set_id(
            session=session, game_set_id=game_set.id, name=pawn_new_name
        )
        if exist_pawn:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    pawn = await Pawn.get_by_name_and_game_set_id(
        session=session, game_set_id=game_set.id, name=pawn_name
    )
    if not (user.id == pawn.user_id or user.id == game_set.owner.id):
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    if pawn_new_name:
        await Pawn.update(session=session, id=pawn.id, name=pawn_new_name)
    await PawnMeta.update(
        session=session, id=pawn.meta.id, **pawn_meta.dict(exclude_unset=True)
    )

    await session.flush()
    await session.commit()
    return PawnModel.from_orm(pawn)


@router.post(
    "/{game_set_short_url}/{pawn_name}",
    response_model=PawnModel,
    status_code=201,
)
async def move_pawn(
    pawn_name: constr(max_length=30),
    pawn_move: PawnMoveModel,
    game_set: GameSet = Depends(get_current_game_set),
    _: User = Depends(check_user),
    session: AsyncSession = Depends(get_db),
):
    new_position = pawn_move.new_position
    map_meta: MapMeta = game_set.meta.map.meta

    pawn = await Pawn.get_by_name_and_game_set_id(
        session=session, game_set_id=game_set.id, name=pawn_name
    )
    pawn_meta: PawnMeta = pawn.meta

    if new_position[0] <= (map_meta.len_x - pawn_meta.size_x) and new_position[
        1
    ] <= (map_meta.len_y - pawn_meta.size_y):
        pawn.meta.position = new_position
        await session.commit()
    return PawnModel.from_orm(pawn)


@router.delete(
    "/{game_set_short_url}/{pawn_name}",
    response_model=PawnModel,
)
async def delete_pawn(
    pawn_name: constr(max_length=30),
    game_set: GameSet = Depends(get_current_game_set),
    user: User = Depends(check_user),
    session: AsyncSession = Depends(get_db),
):
    pawn = await Pawn.get_by_name_and_game_set_id(
        session=session, game_set_id=game_set.id, name=pawn_name
    )
    if pawn:
        if not (user.id == pawn.user_id or user.id == game_set.owner.id):
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
        await session.delete(pawn)
        await session.commit()

        return PawnModel.from_orm(pawn)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
