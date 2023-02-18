from fastapi import APIRouter, Depends

from dnd.database.schemas.users import User
from dnd.models.game_set import GameSetModel, UserGameSetModel
from dnd.models.map import MapsModel
from dnd.procedures.auth import check_user

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/maps", response_model=MapsModel)
async def get_user_maps(
    user: User = Depends(check_user),
):
    return MapsModel(maps=user.maps)


@router.get("/game_sets")
async def get_user_game_sets(
    user: User = Depends(check_user),
) -> list[GameSetModel]:
    return [GameSetModel.from_orm(game_set) for game_set in user.game_sets]


@router.get("/in_games")
async def get_user_in_games(
    user: User = Depends(check_user),
) -> list[UserGameSetModel]:
    return [
        UserGameSetModel.from_orm(mapper.game_set) for mapper in user.in_games
    ]
