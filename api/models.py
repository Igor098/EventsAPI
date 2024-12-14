from pydantic import BaseModel, ConfigDict


class EventSchema(BaseModel):
    id: int
    category_id: int
    location_id: int
    name: str
    date_start: str
    date_end: str
    logo: str
    small_logo: str
    event_description: str
    min_price: int
    max_price: int
    age_restriction: str
    places: list
    model_config = ConfigDict(from_attributes=True)


class EventsResponse(BaseModel):
    loc_id: int
    limit: Optional[int] = 20
    offset: Optional[int] = 0