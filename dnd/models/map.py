from pydantic import BaseModel, conint


class MapMetaLenModel(BaseModel):
    len_x: conint(ge=10, le=1000)
    len_y: conint(ge=10, le=1000)


class MapMetaModel(MapMetaLenModel):
    image_short_url: str | None
    len_x: int
    len_y: int

    class Config:
        orm_mode = True


class MapModel(BaseModel):
    name: str
    meta: MapMetaModel

    class Config:
        orm_mode = True


class MapsModel(BaseModel):
    maps: list[MapModel]
