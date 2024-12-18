from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class PlaceSchema(BaseModel):
    name: str
    address: str


class EventSchema(BaseModel):
    event_id: int
    category_id: int
    location_id: int
    name: str
    date_start: str
    date_end: str
    logo: str
    logo_width: int
    logo_height: int
    small_logo: str
    small_logo_width: int
    small_logo_height: int
    event_description: Optional[str]
    is_free: bool
    min_price: Optional[int]
    max_price: Optional[int]
    age_restriction: str
    places: List[PlaceSchema]
    model_config = ConfigDict(from_attributes=True)


class CategorySchema(BaseModel):
    category_id: int
    category_name: str
    model_config = ConfigDict(from_attributes=True)