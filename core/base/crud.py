# # Native # #
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
# # Installed # #
from fastapi_pagination.ext.async_sqlmodel import paginate
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlmodel import SQLModel, and_, select, func, or_
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import Select, SelectOfScalar

# # Package # #
from core.settings import Params, Page

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)
T = TypeVar("T", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(
        self, db_session: AsyncSession, *, id: Union[UUID, str]
    ) -> Optional[ModelType]:
        response = await db_session.exec(
            select(self.model).where(
                self.model.id == id).options(selectinload('*'))
        )
        return response.first()

    async def get_by_ids(self, db_session: AsyncSession, list_ids: List[Union[UUID, str]],) -> Optional[List[ModelType]]:  # noqa
        response = await db_session.exec(select(self.model).where(self.model.id.in_(list_ids)))
        return response.all()

    async def get_count(
        self, db_session: AsyncSession,
        filters: Union[Dict[str, Any], None] = None,
    ) -> Optional[ModelType]:
        sub_where, _ = await self.__get_sub_query_filters(filters=filters)
        response = await db_session.exec(
            select(func.count()).select_from(select(self.model).where(
                *sub_where).subquery())
        )
        return response.one()

    async def get_all(
        self, db_session: AsyncSession
    ) -> List[ModelType]:
        response = await db_session.exec(
            select(self.model).order_by(self.model.id)
        )
        return response.all()

    async def get_multi(
        self, db_session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        response = await db_session.exec(
            select(self.model).offset(skip).limit(
                limit).order_by(self.model.id)
        )
        return response.all()

    async def get_multi_paginated(
        self, db_session: AsyncSession, *,
        filters: Optional[Dict[str, Any]] = None,
        scope: Optional[List[str]] = None,
        params: Optional[Params] = Params(),
        query: Optional[Union[T, Select[T], SelectOfScalar[T]]] = None
    ) -> Page[ModelType]:
        sub_where, join_table = await self.__get_sub_query_filters(filters=filters)
        select_fields = await self.__get_select_fields(scope=scope)
        if query is None:
            query = select(*select_fields)
            for table in join_table:
                query = query.join(*table).select_from(self.model)
            query = query.where(
                *sub_where).options(selectinload('*'))
        return await paginate(db_session, query, params)

    async def create(
        self, db_session: AsyncSession,
        *,
        obj_in: Union[CreateSchemaType, ModelType],
        created_by: Optional[Union[UUID, str]] = None
    ) -> ModelType:
        db_obj = self.model.from_orm(obj_in)  # type: ignore
        db_obj.created_at = datetime.utcnow()
        db_obj.updated_at = datetime.utcnow()
        if created_by:
            db_obj.created_by = created_by

        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    # TODO: improve this method. Don't update db with same values, add updated_at
    async def update(
        self,
        db_session: AsyncSession,
        *,
        obj_current: ModelType,
        obj_new: Union[UpdateSchemaType, Dict[str, Any], ModelType],
    ) -> ModelType:
        obj_data = jsonable_encoder(obj_current)

        if isinstance(obj_new, dict):
            update_data = obj_new
        else:
            # This tells Pydantic to not include the values that were not sent
            update_data = obj_new.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(obj_current, field, update_data[field])
            if field == "updated_at":
                setattr(obj_current, field, datetime.utcnow())

        db_session.add(obj_current)
        await db_session.commit()
        await db_session.refresh(obj_current)
        return obj_current

    async def remove(
        self, db_session: AsyncSession, *, id: Union[UUID, str]
    ) -> ModelType:
        response = await db_session.exec(select(self.model).where(self.model.id == id))
        obj = response.one()
        await db_session.delete(obj)
        await db_session.commit()
        return obj

    async def __get_sub_query_filters(self, filters: Union[Dict[str, Any], None]):
        sub_query = [and_()]
        join_table = []
        if filters:
            if filters.get("base", False):
                if filters["base"].get("date_start", False):

                    sub_query.append(and_(
                        self.model.created_at >= filters["base"]["date_start"],
                        self.model.created_at <= filters["base"]["date_end"]
                    ))
                    del filters["base"]["date_start"]
                if filters["base"].get("date_end"):
                    del filters["base"]["date_end"]
                for key, value in filters["base"].items():
                    for v in value:
                        sub_query.append(and_(getattr(
                            self.model, key) == v
                        ))
            if filters.get("extend", False):
                for filter_data in filters["extend"]:
                    join_table.append(
                        filter_data["table"]) if filter_data["table"] not in join_table else ...
                    multi_filters = []
                    for value in filter_data["value"]:
                        multi_filters.append(getattr(
                            filter_data["table"][0], filter_data["field"]) == value)
                    sub_query.append(or_(*multi_filters))

        return sub_query, join_table

    async def __get_select_fields(
        self, scope: Union[List[str], None]
    ) -> list[Type[ModelType]]:
        select_fields = []
        if scope:
            for field in scope:
                select_fields.append(getattr(self.model, field))
        else:
            select_fields.append(self.model)
        return select_fields
