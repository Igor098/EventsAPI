from typing import Optional

from pydantic import BaseModel


class Event(BaseModel):
    id: str
    idfull: str
    pref: str
    cat_id: str
    cat_url: str
    loc_id: str
    name: str
    date_start: str
    date_end: str
    logo: str
    logo_p: str
    anons: str
    is_free: str
    min_price: str
    max_price: str
    age: str
    vip: str
    places: list


class EventsResponse(BaseModel):
    loc_id: int
    limit: Optional[int] = 20
    offset: Optional[int] = 0