from sqlalchemy.orm import mapped_column
from typing_extensions import Annotated
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs


class PrintMixin():
    def __repr__(self) -> str:
        return f'{type(self)} - {self.id}'
    
    def __str__(self) -> str:
        return f'{type(self)} - {self.id}' 


id_field = Annotated[
    int, mapped_column(primary_key=True, index=True, autoincrement=True, sort_order=-999, comment='id')
]    

class Base(DeclarativeBase, AsyncAttrs, PrintMixin):
    schema = None

    id: Mapped[id_field]

    @classmethod
    def get_primary_key_path(cls) -> str:
        return f'{cls.__tablename__}.id'


