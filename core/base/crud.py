# type: ignore
import operator
import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import (
    ARRAY,
    and_,
    bindparam,
    delete,
    func,
    nulls_last,
    or_,
    select,
    text,
    true,
    update,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Query, selectinload
from sqlalchemy.orm.attributes import InstrumentedAttribute  # noqa
from sqlalchemy.sql import ColumnElement
from sqlalchemy.sql.expression import false

from core.base.model import BaseUUIDModel
from core.base.schema import IBaseUser, PaginateQueryParams
from core.constants import EMPTY_VALUE
from core.logger import logger
from core.settings import Page, Params
from core.utils import (
    empty_str_to_none,
    escape_special_chars_for_tsquery,
    exec_count,
    flatten_single_element_row,
    paginate,
    separate_nulls,
)


class Base:
    pass


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)
T = TypeVar("T", bound=Base)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    @staticmethod
    def __escape_special_chars_for_tsquery(string: str) -> str:
        # Regex pattern to match special characters that need to be escaped in tsquery
        pattern = r'([&|"\':!*()])'
        # Replace each special character with its escaped version
        return re.sub(pattern, r"\\\1", string)

    @staticmethod
    def __validate_values(filters: dict) -> dict:
        return {key: empty_str_to_none("cls", value) for key, value in filters.items()}

    @staticmethod
    def __separate_nulls(values: list) -> tuple[list, bool]:
        null_values = (EMPTY_VALUE, None, "", [None])
        non_null_values = [v for v in values if v not in null_values]
        nulls_present = len(non_null_values) != len(values)
        return non_null_values, nulls_present

    def __pre_update(
        self,
        *,
        update_data: dict[str, Any],
        user: Optional[IBaseUser] = None,
    ):
        """
        This is a private method invoked by the update method. It's responsible for executing
        the pre_update method and subsequently calling the __update_changelog method. The rationale
        for this sequence is that the pre_update method might alter or add fields that need to be
        tracked by the changelog.
        """

        # Check if the model is a subclass of BaseUUIDModel and add changelog entries
        if issubclass(self.model, BaseUUIDModel):
            # todo прокидывать id если нужен запрос значения до обновления
            self.__update_changelog(update_data=update_data, user=user)

    def __update_changelog(
        self,
        *,
        update_data: dict[str, Any],
        user: Optional[IBaseUser] = None,
    ):
        change_list = []
        for field_name, field_value in update_data.items():
            if getattr(self.model, "Meta", lambda: None)() is not None:
                try:
                    if field_name in self.model.Meta.log_fields:
                        value = field_value.value if isinstance(field_value, Enum) else field_value
                        change_list.append(
                            {
                                "updated_at": datetime.utcnow().isoformat(),
                                "updated_by": user.email if user else "unknown",
                                "attribute": field_name,
                                # Для предыдущего значения, нужно получать его либо с фронта, либо делать запрос к дб.
                                # "previous_value": "",
                                "current_value": value,
                            }
                        )
                except Exception as e:
                    logger.exception(f"{e}")
        if change_list:
            update_data["changelog"] = self.model.changelog + change_list

    def __pick_updated_data(self, obj_new) -> dict:
        """About unset.

        This tells Pydantic to not include the values that were not sent
        update_data = obj_new.dict(exclude_unset=True)

        В валидаторе  мб логика обновляющая другое поле: Если 'supervisor_status' == 'a', то 'required_review' = 'b'
        obj_new.dict(exclude_unset=True) будет учитывать поле required_review проставленное в валидаторе как unset
        obj_new.dict(exclude_none=True) не будет учитывать пустые значения переданые пользователем,
        например, что бы удалить комментарий comment='' станет comment=None в pre валидаторе и будет удалён
        obj_new.dict(exclude_none=True)
        """
        received_data = obj_new.dict(exclude_unset=True)
        update_data = obj_new.dict(exclude_none=True)
        received_empty_values = {key: received_data[key] for key in set(received_data) - set(update_data)}
        if received_empty_values:
            update_data.update(received_empty_values)
        return update_data

    def _filter_is_deleted(self, where: list, show_deleted: bool):
        if show_deleted is False and "is_deleted" in self.model.__table__.columns:
            where.append(self.model.is_deleted == false())

    async def build_query(  # noqa C901
        self,
        id: Optional[UUID | str | list[UUID | str]] = None,
        query_params: PaginateQueryParams = None,
        # Базовый запрос удобен, но может сломать идею делать весь запрос в один приём,
        query: Optional[T | Query] = None,
        visibility_group: Optional[dict] = None,
        joined_load: Optional[Any] = None,
        include_model: Optional[list] = [],  # noqa
        exclude_model: Optional[list] = [],  # noqa
        disable_joinedload: Optional[bool] = False,
        joined_models: Optional[list] = None,
        disable_sorting: Optional[bool] = False,
        show_deleted: Optional[bool] = False,
    ):
        # todo сюда передаем все из get что нужно для создание запроса
        #  т.е get только вызывает эту функцию и потом выполняет полученный запрос

        #  в целом запрос состоит из
        #  select
        #  join
        #  where
        #  sort
        #  paginate
        #  options хотелось бы билдить запрос в один прием, так что бы если where прописан один раз то в него сразу
        #  все фильтры, до этого были множественные добавления where

        #  кажется с можно сделать общий mapping_filters и дать возможность его переопределять через хук.
        #  А path пути писать в каждой ручке отдельно.  мб сделать логику, если нет кастомного описания то обращаться к
        #  общему.
        #  Вероятно проще брать модель просто по префиксу колонки через общий реестр, мб проще поправить все имена
        #  по стандарту, чем переносить кастомную логику.
        #  возможно написать автоимпорт ifilter к модели

        #  берем модель по префиксу названия колонки и джоиним если нужно

        join = []
        where = []
        sort = []
        options = []  # noqa
        if joined_models is None:
            joined_models = []
        if query is None:
            query = select(self.model)

        self._filter_is_deleted(where, show_deleted)

        if visibility_group:
            if visibility_group.get("is_null"):
                where.append(
                    or_(self.model.owner_id.in_(visibility_group["users"]), self.model.owner_id == None)  # noqa
                )
            else:
                where.append(self.model.owner_id.in_(visibility_group["users"]))

            if hasattr(self.model, "owner_id_extra"):
                if visibility_group.get("is_null"):
                    where.append(
                        or_(
                            self.model.owner_id_extra.in_(visibility_group["users"]),
                            self.model.owner_id_extra == None,  # noqa
                        )
                    )
                else:
                    where.append(self.model.owner_id_extra.in_(visibility_group["users"]))

        if id:
            if isinstance(id, list):
                # query = query.where(self.model.id.in_(id))
                where.append(self.model.id.in_(id))
            elif isinstance(id, str) or isinstance(id, UUID):
                # query = query.where(self.model.id == id)
                where.append(self.model.id == id)
            # при вызове get по id нужен как минимум joined_load
            # response = await db_session.execute(query)
        elif query_params:
            if (search := query_params.search) is not None:
                value = search[0]["value"]
                search_words = [escape_special_chars_for_tsquery(word).strip() for word in value]
                tsquery = " | ".join(search_words)
                concatenated_attributes = func.concat_ws(" ", *[getattr(row["model"], row["column"]) for row in search])
                where.append(func.to_tsvector(concatenated_attributes).op("@@")(func.to_tsquery(tsquery)))
                for row in search:
                    join.append({key: row[key] for key in ["model", "path"]})

            if (period := query_params.period) is not None:
                for row in period:
                    start_date, end_date = row["value"]
                    if column := getattr(row["model"], row["column"], False):
                        # не у всех моделей есть created_at
                        where.extend([column >= start_date, column < end_date + timedelta(days=1)])
                        join.append({key: row[key] for key in ["model", "path"]})

            # if "scope" in query_params:  todo без scope на первом этапе
            #     for field in query_params["scope"]:
            #         query = query.with_entities(getattr(self.model, field))

            for number_operator in ("gt", "lt", "eq"):
                if (number_filters := getattr(query_params, number_operator)) is not None:
                    for row in number_filters:
                        # ("gt", "lt", "eq") -> ("ge", "le", "eq")
                        op = getattr(operator, number_operator.replace("t", "e"))
                        column = getattr(row["model"], row["column"])
                        where.append(op(column, row["value"]))
                        join.append({key: row[key] for key in ["model", "path"]})

            if (filters := query_params.filters) is not None:
                for row in filters:
                    significant_values, nulls = separate_nulls(row["value"])
                    column = getattr(row["model"], row["column"])
                    multi_filters = []
                    if isinstance(column.comparator.type, ARRAY):
                        # todo потестить массивы
                        #  например в новом мастере будет работать Product.country_purchase
                        #  можно будет потестить на нем
                        for value in significant_values:
                            multi_filters.append((getattr(column, "any")(value)))  # noqa
                    else:
                        multi_filters.append(column.in_(tuple(significant_values)))
                    add_nulls = and_(*multi_filters) if not nulls else or_(column.is_(None), and_(*multi_filters))
                    where.append(add_nulls)
                    join.append({key: row[key] for key in ["model", "path"]})

            # if (sorting := query_params.ascending or query_params.descending) is not None:
            for sorting in ("ascending", "descending"):
                if (sort_row := getattr(query_params, sorting)) is not None:
                    sort_row = sort_row[0]
                    column = getattr(sort_row["model"], sort_row["column"])
                    sort.append(nulls_last(column.asc() if sorting == "ascending" else column.desc()))
                    join.append({key: sort_row[key] for key in ["model", "path"]})

        # query = query.order_by(nulls_last(self.model.created_at))
        # todo вынести в отдельную функцию
        joined_models.append(self.model)
        for join_model in join:
            model = join_model["model"]
            if model in joined_models:
                continue
            path = join_model["path"]
            if path is not None:
                for models in path:
                    # xxx: альясы не используются,
                    # например при джоине пользователей к карточкам как КМ и второй раз как SEO
                    # могут быть артефакты в фильтрации
                    if isinstance(models, dict):
                        path_model = models["model"]
                        condition = models["condition"]
                    else:
                        path_model = models[-1]
                        condition = models[0] == models[1]

                    if path_model in joined_models:
                        continue
                    joined_models.append(path_model)
                    query = query.outerjoin(path_model, condition)
            else:
                joined_models.append(model)
                query = query.outerjoin(model)
        if not disable_sorting and not sort and getattr(self.model, "created_at", False):
            sort = [nulls_last(self.model.created_at.desc())]
        if where:
            query = query.where(*where)
        if sort:
            query = query.order_by(*sort)
        used_relations = set()
        if joined_load is None:
            joined_load = []

        else:
            for row in joined_load:
                path = row.path.path
                relation = path[1].key  # todo docs
                used_relations.add(relation)

        # todo кажется нужно добавлять джоинлоад только для релейшенов на которые есть записи в Iread,
        #  Подумать как связать имя релейшена и префикс колонки Iread.
        #  Например, пользователь может называться owner, user__full_name и т.д.
        mapper = inspect(self.model)
        try:
            linked_properties = query_params.Config.linked_properties
        except AttributeError:
            linked_properties = None
        for relation_property in mapper.relationships:
            relation_name = relation_property.key
            if relation_name in used_relations:
                continue
            if all(
                (
                    not disable_joinedload,
                    linked_properties is None or relation_name in query_params.Config.linked_properties,
                    relation_name not in exclude_model,
                )
            ) or (disable_joinedload and relation_name in include_model):
                joined_load.append(selectinload(getattr(self.model, relation_name)))
                used_relations.add(relation_name)
        if joined_load:
            query = query.options(*joined_load)
        return query

    async def generate_sql(
        self,
        *,
        id: Optional[UUID | str | list[UUID | str]] = None,
        query_params: PaginateQueryParams = None,
        query: Optional[T | Query] = None,
        visibility_group: Optional[dict] = None,
        joined_load: Optional[Any] = None,
        include_model: Optional[list] = [],  # noqa
        exclude_model: Optional[list] = [],  # noqa
        joins: Optional[bool] = True,
        disable_joinedload: bool = False,
        joined_models: Optional[list] = None,
    ) -> str:
        if not joins:
            disable_joinedload = True

        query = await self.build_query(
            id=id,
            query_params=query_params,
            query=query,
            visibility_group=visibility_group,
            joined_load=joined_load,
            include_model=include_model,
            exclude_model=exclude_model,
            disable_joinedload=disable_joinedload,
            joined_models=joined_models,
        )

        compiled_query = query.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})

        return str(compiled_query)

    async def get(
        self,
        db_session: AsyncSession,
        *,
        id: Optional[UUID | str | list[UUID | str]] = None,
        query_params: PaginateQueryParams = None,
        query: Optional[T | Query] = None,
        visibility_group: Optional[dict] = None,
        is_paginate: Optional[bool] = True,
        mapping: Optional[Any] = None,  # todo как это должно обрабатываться?
        # todo попробовать убрать любой джоинлоад, добавлять модель в select
        #  и раскладывать присоединенные модели в валидаторе в relation свойства
        #  будет быстрее
        joined_load: Optional[Any] = None,
        include_model: Optional[list] = [],  # noqa
        exclude_model: Optional[list] = [],  # noqa
        joins: Optional[bool] = True,
        disable_joinedload: bool = False,  # todo joins непонятное название, везде использовать disable_joinedload
        first=False,
        joined_models: Optional[list] = None,
    ) -> Optional[ModelType | list[ModelType] | Page[ModelType]]:
        # todo если билдим запрос здесь, то в других местах можем переиспользовать?
        #  возможно нужна более универсальная функция
        #  возможно нужен отдельный класс генератор запроса
        if not joins:
            disable_joinedload = True

        # todo оставить хук для любых where в конце функции
        query = await self.build_query(
            id=id,
            query_params=query_params,
            query=query,
            visibility_group=visibility_group,
            joined_load=joined_load,
            include_model=include_model,
            exclude_model=exclude_model,
            disable_joinedload=disable_joinedload,
            joined_models=joined_models,
        )

        if hasattr(query_params, "page") and hasattr(query_params, "size"):
            params = Params(page=query_params.page, size=query_params.size)
            return await paginate(db_session, query, params)  # todo свой пагинейт через get_count

        if first:
            query = query.limit(1)
        response = await db_session.execute(query)
        items = response.unique().all()
        items = flatten_single_element_row(items)
        if first and len(items) == 1:
            return items[0]
        return items
        # return Page(items=response.scalars().all(), page=1, total_count=None)

    async def get_by_column_and_value(
        self, db_session: AsyncSession, *, filter_data: dict, first=False, joined_load=None, or_value=False
    ) -> Optional[ModelType]:
        # todo говорили что метод get будет один на crud класс, видение поменялось?
        for k, v in filter_data.items():
            if not isinstance(v, list):
                filter_data[k] = [v]
        query = select(self.model)
        where = []
        for key, value in filter_data.items():
            significant_values, nulls = separate_nulls(value)
            if nulls:
                where.append(getattr(self.model, key) == None)  # noqa
            if significant_values:
                where.append(getattr(self.model, key).in_(significant_values))
        if or_value:
            query = query.where(or_(*where))
        else:
            query = query.where(*where)
        if joined_load:
            query = query.options(*joined_load)

        if first:
            query = query.limit(1)
        response = await db_session.execute(query)
        items = response.unique().all()
        items = flatten_single_element_row(items)
        if first and len(items) == 1:
            return items[0]
        return items

    async def get_count(
        self,
        db_session: AsyncSession,
        query: Optional[T | Query] = None,
        query_params: PaginateQueryParams = None,
        # constraint: Optional[list] = None,
        visibility_group: Optional[list] = None,
        joined_models: Optional[list] = None,
    ) -> Optional[ModelType]:
        """Префильтры используют логику get_count в которой фильтрация работает не так как в get. И считается неправильно, там inner join вместо left, нет числовых фильтров.
        Также в пагинации нужен count, чтобы показывать общее количество страниц.
        Хорошо было бы делать это одинаково и правильно. Чтобы парсить фильтры используется PaginateQueryParams и он использует IFilters.
        Для единообразия работает так же через PaginateQueryParams. Эти параметры придется обяъявлять везде где нужен count с фильтрами
        """
        if query is None:
            query = await self.build_query(
                query_params=query_params,
                query=query,
                visibility_group=visibility_group,
                disable_joinedload=True,
                joined_models=joined_models,
            )
        count = await exec_count(db_session, query)
        return count

    async def save_all(
        self,
        db_session: AsyncSession,
        all_obj: list[ModelType],
        user: Optional[IBaseUser] = None,
        refresh=False,
    ):
        for obj in all_obj:
            obj.created_at = obj.created_at if obj.created_at else datetime.utcnow()
            obj.updated_at = datetime.utcnow()
            if user:
                obj.created_by = obj.created_by if obj.created_by else user.id
                obj.updated_by = user.id
        db_session.add_all(all_obj)
        await db_session.commit()
        if refresh:
            for obj in all_obj:
                await db_session.refresh(obj)
        return all_obj

    async def create(
        self,
        db_session: AsyncSession,
        *,
        obj_in: List[CreateSchemaType] | List[ModelType],
        user: Optional[IBaseUser] = None,
        refresh=True,
        list_res=False,
        **kwargs,  # visibility group
    ) -> list[ModelType]:
        # todo обсудить, версию через insert, во многих случаях она будет проще и быстрее
        all_obj = []
        if not isinstance(obj_in, list):
            obj_in = [obj_in]
        for obj in obj_in:
            db_obj = self.model(**obj.dict())  # type: ignore
            if hasattr(self.model, "created_at"):
                db_obj.created_at = datetime.utcnow()
                db_obj.updated_at = datetime.utcnow()
            if user:
                db_obj.created_by = user.id
                db_obj.updated_by = user.id
            all_obj.append(db_obj)

        db_session.add_all(all_obj)
        await db_session.commit()
        if refresh:
            for obj in all_obj:
                await db_session.refresh(obj)
        if list_res:
            return all_obj
        # xxx: чаще всего потом проверяем список это или единичный объект, выглядит проще всегда список отдавать
        if len(all_obj) == 1:
            return all_obj[0]
        return all_obj

    async def update(
        self,
        db_session: AsyncSession,
        *,
        id: Optional[list[UUID]] = None,
        obj_new: UpdateSchemaType | dict[str, Any] | ModelType,
        user: Optional[IBaseUser] = None,
        query_params: PaginateQueryParams = None,
        visibility_group: Optional[dict] = None,
        **kwargs,  # todo передаётся visibility_group но не обрабатывается
    ):
        if id is None and query_params is None:
            raise NotImplementedError("One of id or query_params is required")
        elif id is not None and query_params is not None:
            raise NotImplementedError("One of id or query_params is allowed")
        # obj_data = jsonable_encoder(obj_current)
        if isinstance(obj_new, dict):
            obj_new = obj_new
        else:
            obj_new = self.__pick_updated_data(obj_new)
        # make copy of update_data to avoid changing the original data outside of this function
        obj_new = obj_new.copy()

        if user:
            obj_new["updated_by"] = user.id

        # call pre_update hook

        if query_params:
            delattr(query_params, "page")
            delattr(query_params, "size")
            delattr(query_params, "scope")
            ids_only = select(self.model.id)
            ids_query = await self.build_query(
                query_params=query_params,
                query=ids_only,
                visibility_group=visibility_group,
                disable_joinedload=True,
                disable_sorting=True,
            )
            subquery = ids_query
            where_in = (self.model.id.in_(subquery),)
        else:
            self.__pre_update(update_data=obj_new, user=user)
            additional_filters = []
            where_in = self.model.id.in_(bindparam("_id")), *additional_filters

        stmt = (
            update(self.model)
            .where(*where_in)
            .values(
                {
                    # if value is an expression, don't bind it, just use as is
                    field: value if isinstance(value, ColumnElement) else bindparam(field)
                    for field, value in obj_new.items()
                    # Update only existing columns in table
                    if hasattr(self.model, field)
                }
            )
        )

        # Prepare bindings except the values that are ColumnElement
        bindings = {field: value for field, value in obj_new.items() if not isinstance(value, ColumnElement)}
        values = {"_id": id} | bindings if id else bindings
        await db_session.execute(stmt, values)
        await db_session.commit()

    async def remove(
        self,
        db_session: AsyncSession,
        id: UUID | List[UUID],
        *,
        visibility_group: Optional[dict] = None,
        query=None,
        is_soft_delete: Optional[bool] = False,
    ) -> ModelType:
        # response = await db_session.execute(
        #     select(self.model).where(self.model.id == id)
        # )
        # obj = response.unique().one()
        # await db_session.delete(obj)
        # await db_session.commit()
        # return obj
        additional_filters = []
        if visibility_group:
            for key, value in visibility_group.items():
                additional_filters.append(getattr(self.model, key).in_(value))
        else:
            additional_filters.append(true())
        # todo для локального запуска
        # ----
        if query is None:
            query = delete(self.model)
        if id is None:
            raise NotImplemented  # noqa todo какие кейсы на пустой id? выглядит уязвимо
        if not isinstance(id, list):
            id = [id]
        query = query.where(self.model.id.in_(id))
        # ----
        query = query.where(*additional_filters)

        # if filters:
        #     filters_where, join_table, _ = await self.__get_query_filters(filters=filters)
        #     query = query.where(*filters_where)
        await db_session.execute(query)
        await db_session.commit()

    async def raw(
        self,
        db_session: AsyncSession,
        *,
        query: str,
    ) -> Optional[ModelType]:
        query = select(self.model).from_statement(text(query))
        response = await db_session.execute(query)
        return response.unique().all()


class AnalyticsMixin:
    def _generate_date_range(self, days: int) -> tuple[datetime, list[str]]:
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        start_date = end_date - timedelta(days=int(days) - 1)

        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)

        return start_date, dates

    def _create_response_structure(self, labels: list, dates: list) -> dict:
        return {"label": labels, "date": dates, "data": [[0] * len(dates) for _ in labels]}

    async def _get_time_series_data(
        self,
        db_session: AsyncSession,
        model: Type[Any],
        filters: list,
        value_getters: list[str],
        labels: list[str],
        limit: int,
    ) -> dict:
        # Generate date range
        start_date, dates = self._generate_date_range(limit)

        # Build and execute query
        query = (
            select(model)
            .where(*filters)
            .where(and_(model.date >= start_date, model.date < datetime.now().date()))
            .order_by(model.date.desc())
        )

        response = await db_session.execute(query)
        results = response.scalars().all()

        # Create response structure
        data = self._create_response_structure(labels=labels, dates=dates)

        # Create date to index mapping
        date_to_index = {date: idx for idx, date in enumerate(dates)}

        # Fill in the data
        for row in results:
            date_str = row.date.strftime("%Y-%m-%d")
            if date_str in date_to_index:
                idx = date_to_index[date_str]
                for idx_col, value_getter in enumerate(value_getters):
                    data["data"][idx_col][idx] = getattr(row, value_getter)

        return data

    @staticmethod
    async def _get_ranged_data(
        db_session: AsyncSession,
        model: Type[Any],
        filters: list,
        value_getters: list,
        labels: list[str],
        limit: int,
    ) -> dict:

        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        start_date = end_date - timedelta(days=int(limit) - 1)

        query = (
            select(model)
            .where(*filters)
            .where(and_(model.date >= start_date, model.date < datetime.now().date()))
            .order_by(model.date.desc())
        )
        response = await db_session.execute(query)
        results = list(response.scalars().all())

        date_data_map = {}
        for result in results:
            date_str = result.date.strftime("%Y-%m-%d")
            date_data_map[date_str] = [getattr(result, value) for value in value_getters]

        data = []
        dates = sorted({result.date.strftime("%Y-%m-%d") for result in results})
        for date in dates:
            data.append(date_data_map.get(date, [0, 0, 0, 0, 0]))

        return {"label": labels, "date": dates, "data": data}
