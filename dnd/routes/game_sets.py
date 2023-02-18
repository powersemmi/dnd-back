from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from hashids import Hashids
from sqlalchemy.ext.asyncio import AsyncSession

from dnd.database.db import get_db
from dnd.database.schemas.game_sets import GameSet, GameSetMeta
from dnd.database.schemas.maps import Map
from dnd.database.schemas.users import User, UserInGameset
from dnd.models.game_set import (
    CreateGameSetRequestModel,
    GameSetModel,
    UpdateGameSetRequestModel,
)
from dnd.procedures.auth import check_user
from dnd.procedures.game_set import get_current_game_set
from dnd.utils.crypto import get_shortcut

router = APIRouter(prefix="/game_set", tags=["game_set"])


@router.put(
    "/", response_model=GameSetModel, status_code=status.HTTP_201_CREATED
)
async def create_game_set(
    game_set: CreateGameSetRequestModel,
    user: User = Depends(check_user),
    session: AsyncSession = Depends(get_db),
    shortcut: Hashids = Depends(get_shortcut),
) -> GameSetModel:
    game_set_id = await GameSet.get_next_id(session=session)
    short_url = shortcut.encode(game_set_id)
    new_game_set = await GameSet.create(
        session=session,
        game_set_id=game_set_id,
        owner_id=user.id,
        name=game_set.name,
        short_url=short_url,
    )
    map_id = None
    if game_set.map_name is not None:
        map = await Map.get_by_name_and_user_id(
            session=session, user_id=user.id, name=game_set.map_name
        )
        map_id = map.id
        if not map_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selected map not found",
            )
    game_set_meta = await GameSetMeta.create(
        game_set_id=new_game_set.id,
        map_id=map_id,
        session=session,
    )
    new_game_set.meta = game_set_meta
    await session.commit()
    return GameSetModel.from_orm(new_game_set)


@router.patch(
    "/{game_set_short_url}/",
    response_model=GameSetModel,
    status_code=status.HTTP_201_CREATED,
)
async def update_game_set(
    game_set_data: UpdateGameSetRequestModel,
    user: User = Depends(check_user),
    game_set: GameSet = Depends(get_current_game_set),
    session: AsyncSession = Depends(get_db),
) -> GameSetModel:
    if user.id == game_set.owner.id:
        if data := game_set_data.dict(exclude_unset=True):
            if new_name := data.get("name"):
                await GameSet.update(
                    session=session, id=game_set.id, name=new_name
                )
                data.pop("name")
            new_map_name = data.get("map_name", False)
            if new_map_name or new_map_name is None:
                data.pop("map_name")
            if isinstance(new_map_name, str):
                new_map = await Map.get_by_name_and_user_id(
                    session=session,
                    user_id=user.id,
                    name=new_map_name,
                )
                if not new_map:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Map not found",
                    )
                data["map_id"], data["map"] = new_map.id, new_map
            elif new_map_name is None:
                data["map_id"] = data["map"] = None
            updated_meta = await GameSetMeta.update(
                session=session,
                id=game_set.meta.id,
                **{x: data[x] for x in data if x != "map"},
            )
            updated_meta.map = data["map"]
            game_set.meta = updated_meta

        return GameSetModel.from_orm(game_set)
    raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)


@router.get("/{game_set_short_url}/", response_model=GameSetModel)
async def get_game_set(
    user: User = Depends(check_user),
    game_set: GameSet = Depends(get_current_game_set),
):
    if (
        user.id in [user.user_id for user in game_set.users_in_game]
        or user.id == game_set.owner.id
    ):
        res: GameSetModel = GameSetModel.from_orm(game_set)
        if user.id == game_set.owner.id:
            return res
        res.pawns = [
            pawn
            for pawn in res.pawns
            if pawn.user.username == user.username or pawn.meta.visibility
        ]
        return res
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="GameSet not found",
    )


@router.post(
    "/join/{game_set_short_url}/",
    status_code=202,
    responses={
        status.HTTP_406_NOT_ACCEPTABLE: {"status": "not acceptable"},
        status.HTTP_202_ACCEPTED: {"status": "accepted"},
        status.HTTP_304_NOT_MODIFIED: {"status": "not modified"},
    },
)
async def join_to_game(
    user: User = Depends(check_user),
    game_set: GameSet = Depends(get_current_game_set),
    session: AsyncSession = Depends(get_db),
):
    if user.id == game_set.owner.id:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)
    elif user.id in [user.user_id for user in game_set.users_in_game]:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
    user_in_game = await UserInGameset.create(
        session=session, user_id=user.id, game_set_id=game_set.id
    )
    user.in_games.append(user_in_game)
    game_set.users_in_game.append(user_in_game)
    await session.commit()
    return Response(status_code=202, content="accepted")


@router.delete("/{game_set_short_url}/")
async def delete_game_set(
    user: User = Depends(check_user),
    game_set: GameSet = Depends(get_current_game_set),
    session: AsyncSession = Depends(get_db),
):
    if user.id == game_set.owner.id:
        await session.delete(game_set)
        await session.commit()
        return Response(status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
