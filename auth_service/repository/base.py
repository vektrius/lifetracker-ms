from typing import Any, List
from sqlalchemy import ColumnExpressionArgument, Select, select
from database.database import get_session
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

class MultipleObjectsReturned(Exception):
    pass


class ObjectsNotExists(Exception):
    pass

class NotSupportException(Exception):
    pass

SelectQuery = Select[Any]
    
  
  
class BaseRepository():
    model = None

    
    @classmethod
    def get_filter_parametr(cls, field: str, value: Any) -> ColumnExpressionArgument[bool]:
        """ 
        Возращает правильный фильтр с учётом фильтра отношений 
        Пример: UserRepository.get_filter_parametr('transaction__amount', 100) эквивалентно query.filter(User.transaction.any(amount=100)) 
        """
        
        if '__' in field:
            fields = field.split('__')
            if len(fields) > 2:
                raise NotSupportException('Текущая версия не поддерживает глубину больше чем одно отношение.')
            
            related_field = fields[0]
            filter_value_field = fields[1]
            return getattr(cls.model, related_field).any(**{filter_value_field: value})

        return getattr(cls.model, field) == value
        
    @classmethod
    def _filter_query(cls, query: SelectQuery, **filter_by):
        for field, value in filter_by.items():
            filter_parametr = cls.get_filter_parametr(field, value)
            query = query.filter(filter_parametr)
            
        return query
    
    @classmethod
    def _add_select_related_field(cls, query: SelectQuery, fields: List[str]) -> SelectQuery:
        fields = [getattr(cls.model, field) for field in fields]
        return query.options(joinedload(*fields))

    @classmethod
    async def find_all(cls, session: AsyncSession = None, select_related: List[str] = None, **filter_by):
        query = select(cls.model)
        if select_related:
            query = cls._add_select_related_field(query, select_related)
        query = cls._filter_query(query, **filter_by)
        result = await session.execute(query)
        
        return result.scalars().all()
        
    @classmethod
    async def add(cls, session: AsyncSession = None, **kwargs):
        instance = cls.model(**kwargs)
        session.add(instance)
        await session.commit()
            
        return instance
    
    @classmethod
    async def find_one(cls, session: AsyncSession = None, select_related: List[str] = None, **filter_by):
        query = select(cls.model)
        if select_related:
            query = cls._add_select_related_field(query, select_related)
        
        query = cls._filter_query(query, **filter_by)
        
        result = await session.execute(query)
        result = result.scalars().unique().all()
        if len(result) > 1:
            raise MultipleObjectsReturned(f"ожидался 1 объект, а получено два - {result}")
        if len(result) == 0:
            raise ObjectsNotExists("Такого объекта не существует.")

        return result[0]
    
    @classmethod
    async def delete(cls, session: AsyncSession = None, **filter_by):
        query = select(cls.model)
        query = cls._filter_query(query, **filter_by)
        result = await session.execute(query.delete())
        
        return result.scalars().all()

class SessionMixin(): # TODO: Подумать как автоматически выбрать все методы которые зависят от сессии
    @classmethod
    async def find_one(cls, session: AsyncSession = None, *args, **kwargs):
        if not session:
            async with get_session() as session:
                return await super().find_one(session, *args, **kwargs)
            
        return await super().find_one(session, *args, **kwargs)
        
    @classmethod
    async def add(cls, session: AsyncSession = None, *args, **kwargs):
        if not session:
            async with get_session() as session:
                return await super().add(session, *args, **kwargs)
            
        return await super().add(session, *args, **kwargs)
        
    @classmethod
    async def find_all(cls, session: AsyncSession = None, *args, **kwargs):
        if not session:
            async with get_session() as session:
                return await super().find_all(session, *args, **kwargs)
            
        return await super().find_all(session, *args, **kwargs)