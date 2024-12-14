from typing import Annotated

from sqlalchemy.orm import DeclarativeBase, declared_attr, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"


int_pk = Annotated[int, mapped_column(primary_key=True)]
int_uniq = Annotated[int, mapped_column(unique=True, nullable=False)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]
