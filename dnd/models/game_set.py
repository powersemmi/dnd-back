from typing import Optional

from pydantic import BaseModel, constr

from dnd.models.map import MapModel
from dnd.models.pawn import PawnModel


class GameSetPlayerPositionModel(BaseModel):
    x: int
    y: int
    pawn: PawnModel

    class Config:
        orm_mode = True


class GameSetMetaModel(BaseModel):
    map: MapModel | None

    class Config:
        orm_mode = True


class UserInGameModel(BaseModel):
    username: constr(min_length=1, max_length=256)
    full_name: constr(min_length=1, max_length=256) | None

    class Config:
        orm_mode = True


class UsersInGame(BaseModel):
    user: UserInGameModel

    class Config:
        orm_mode = True


class GameSetModel(BaseModel):
    name: str
    short_url: str
    owner: UserInGameModel
    meta: GameSetMetaModel
    pawns: list[PawnModel]
    users_in_game: list[UsersInGame]

    class Config:
        orm_mode = True


class UserGameSetModel(BaseModel):
    name: str
    short_url: str
    owner: UserInGameModel

    class Config:
        orm_mode = True


class GameSetsModel(BaseModel):
    __root__: list[Optional[GameSetModel]]

    class Config:
        orm_mode = True


class UserInGameUpdateRequestModel(BaseModel):
    username: constr(min_length=1, max_length=256)
    full_name: constr(min_length=1, max_length=256) | None


class CreateGameSetRequestModel(BaseModel):
    name: constr(max_length=60)
    map_name: constr(max_length=60) | None


class UpdateGameSetRequestModel(BaseModel):
    name: constr(max_length=60) | None
    map_name: constr(max_length=60) | None
    # users: UserInGameUpdateRequestModel | None
