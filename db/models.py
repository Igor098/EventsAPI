from typing import List

from sqlalchemy import Sequence, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base, str_uniq, int_pk


class Event(Base):
    event_id: Mapped[int_pk]
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.category_id"), nullable=False)
    location_id: Mapped[int]
    name: Mapped[str]
    date_start: Mapped[str]
    date_end: Mapped[str]
    logo: Mapped[str]
    logo_width: Mapped[int]
    logo_height: Mapped[int]
    small_logo: Mapped[str]
    small_logo_width: Mapped[int]
    small_logo_height: Mapped[int]
    event_description: Mapped[str] = mapped_column(nullable=True)
    is_free: Mapped[bool]
    min_price: Mapped[int] = mapped_column(nullable=True)
    max_price: Mapped[int] = mapped_column(nullable=True)
    age_restriction: Mapped[str]
    places = relationship("Place", secondary="events_places", back_populates="events")


class Place(Base):
    place_id: Mapped[int_pk] = mapped_column(Sequence("place_id_seq"))
    place_name: Mapped[str_uniq]
    place_address: Mapped[str]
    events = relationship("Event", secondary="events_places", back_populates="places")


class Category(Base):
    __tablename__ = "categories"
    category_id: Mapped[int_pk]
    category_name: Mapped[str_uniq]


class EventsPlaces(Base):
    __tablename__ = 'events_places'
    event_id: Mapped[int_pk] = mapped_column(ForeignKey("events.event_id"), nullable=False)
    place_id: Mapped[int_pk] = mapped_column(ForeignKey("places.place_id"), nullable=False)