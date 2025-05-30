from enum import Enum

from sqlalchemy import select

from app.model import Permission, Resource, Role
from core.cache.base import CachedValueBase, CachedValueListOrm
from core.cache.schema import (
    PermissionListCacheSchema,
    ResourceListCacheSchema,
    RoleListCacheSchema,
)


class CacheV2KV(Enum):
    km_av = "km_av"
    nomenclature = "nomenclature"
    color = "color"
    size = "size"
    brand = "brand"
    account = "account"
    category = "category"
    object = "object"
    card_tags = "card_tags"


class CacheV2RowList(Enum):
    roles = "roles"
    resources = "resources"
    permissions = "permissions"


class KmAv(CachedValueBase):
    name = CacheV2KV.km_av
    get_distinct_model_args = {
        "sql": """SELECT DISTINCT auth.user.id, auth.user.full_name
                FROM auth.user
                JOIN auth.linkteamuser ON auth.user.id = auth.linkteamuser.user_id
                JOIN auth.team ON auth.team.id = auth.linkteamuser.team_id
                WHERE auth.user.is_active IS TRUE
                AND auth.team.title = 'категорийные менеджеры'
                UNION
                SELECT DISTINCT auth.user.id, auth.user.full_name
                FROM auth.user
                JOIN core.product ON auth.user.id = core.product.owner_id OR auth.user.id = core.product.owner_id_extra
                WHERE auth.user.is_active IS TRUE;"""
    }


class CardTags(CachedValueBase):
    name = CacheV2KV.card_tags
    get_distinct_model_args = {
        "sql": """SELECT core.producttag.id, core.producttag.name
                FROM core.producttag WHERE core.producttag.entity_type = 'card'"""
    }


class NomenclatureTypeAv(CachedValueBase):
    name = CacheV2KV.nomenclature
    get_distinct_model_args = {"model": "product", "attribute": "type_of_nomenclature"}


class ColorAv(CachedValueBase):
    name = CacheV2KV.color
    get_distinct_model_args = {"model": "product", "attribute": "color"}


class SizeAv(CachedValueBase):
    name = CacheV2KV.size
    get_distinct_model_args = {"model": "product", "attribute": "size"}


class BrandAv(CachedValueBase):
    name = CacheV2KV.brand
    get_distinct_model_args = {"model": "brand", "attribute": "title", "pk_name": "id"}


class AccountAv(CachedValueBase):
    name = CacheV2KV.account
    get_distinct_model_args = {"model": "account", "attribute": "title"}


class CategoryAv(CachedValueBase):
    name = CacheV2KV.category
    get_distinct_model_args = {"model": "card", "attribute": "category"}


class ObjectAv(CachedValueBase):
    name = CacheV2KV.object
    get_distinct_model_args = {"model": "card", "attribute": "object"}


class Roles(CachedValueListOrm):
    name = CacheV2RowList.roles
    query = select(Role.id, Role.title)
    schema = RoleListCacheSchema


class Resources(CachedValueListOrm):
    name = CacheV2RowList.resources
    query = select(
        Resource.id, Resource.endpoint, Resource.method, Resource.is_rbac_enabled, Resource.is_visibility_group_enabled
    )
    schema = ResourceListCacheSchema


class Permissions(CachedValueListOrm):
    name = CacheV2RowList.permissions
    query = select(Permission.id, Permission.role_id, Permission.resource_id)
    schema = PermissionListCacheSchema


cache_registry = (
    KmAv,
    NomenclatureTypeAv,
    ColorAv,
    SizeAv,
    BrandAv,
    AccountAv,
    CategoryAv,
    ObjectAv,
    Roles,
    Resources,
    Permissions,
    CardTags,
)
