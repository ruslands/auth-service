import inspect
import json
import uuid

import pytest

import app.constants as constants_module
from core.exceptions import ValidationException
from core.logger import logger


class BaseTest:
    entity = None
    url = None
    create_data = None
    update_data = None
    ifilter = None
    isort = None
    iread = None

    @pytest.mark.asyncio
    async def test_list(self, test_client, auth_data):
        url = f"api/v1/{self.entity}/list"
        # todo нужен ли тест с выключенной мета? кажется что фронт всегда запрашивает с метадатой.
        #  как вариант здесь ускориться
        response = test_client.get(url, headers={"Authorization": f"Bearer {auth_data['access_token']}"})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_meta(self, test_client, auth_data):
        url = f"api/v1/{self.entity}/list"
        response = test_client.get(
            url, params={"meta": True}, headers={"Authorization": f"Bearer {auth_data['access_token']}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_crud(self, test_client, auth_data, create_entity, delete_entity):

        ## Create
        url = f"api/v1/{self.entity}"
        response: dict = create_entity(url, self.create_data)
        if isinstance(response["data"], list):
            id = response["data"][0]["id"]
        else:
            id = response["data"]["id"]
        logger.info("create test passed")
        ## Read
        url = f"api/v1/{self.entity}/{id}"
        response = test_client.get(url, headers={"Authorization": f"Bearer {auth_data['access_token']}"})
        assert response.status_code == 200
        logger.info("read test passed")

        ## Update
        response = test_client.patch(
            url, json=self.update_data, headers={"Authorization": f"Bearer {auth_data['access_token']}"}
        )
        assert response.status_code == 200
        logger.info("update test passed")

        ## Delete
        delete_entity(f"api/v1/{self.entity}/{id}")
        logger.info("delete test passed")

    @pytest.mark.asyncio
    async def test_sort(self, test_client, auth_data, testing):
        operands = ["descending"]
        url = f"api/v1/{self.entity}/list"
        fail = False
        fields = self.iread.Meta.fields
        for key, value in fields.items():
            if value.get("is_sortable") is True:
                for operand in operands:
                    response = test_client.get(
                        url,
                        params={operand: json.dumps(key)},
                        headers={"Authorization": f"Bearer {auth_data['access_token']}"},
                    )
                    if response.status_code != 200:
                        fail = True
                        logger.error(f"sort test failed {key}")
                if testing == "min":
                    break
        assert fail is False

    @pytest.mark.asyncio
    async def test_gt_lt_eq(self, test_client, auth_data):
        operands = ["lt"]  # ["lt, gt, eq"]
        url = f"api/v1/{self.entity}/list"

        fields = self.iread.Meta.fields
        params = {operand: {} for operand in operands}
        for key, value in fields.items():
            if value.get("is_filterable") is True:
                column = value.get("filter_by") or key
                for operand in operands:
                    params[operand].update({column: str(10**7)})
            else:
                continue
        params = {key: json.dumps(value) for key, value in params.items()}
        response = test_client.get(
            url,
            params=params,
            headers={"Authorization": f"Bearer {auth_data['access_token']}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_period(self, test_client, auth_data):
        url = f"api/v1/{self.entity}/list"
        response = test_client.get(
            url,
            params={"period": "2024-01-01:2024-07-01"},
            headers={"Authorization": f"Bearer {auth_data['access_token']}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_filters(self, test_client, auth_data):
        """Тест проверяет заполнение схем фильтрации и маппинга внешних фильтров.

        По умолчанию запрос возращает все записи сущности из базы.
        Если нужны детальные тесты, то их стоит добавить для каждого модуля отдельно."""

        def format_value(value):
            if isinstance(value, bool):
                return str(value).lower()  # лучше переделать на фронте и там отдавать просто булев тип в json
            elif isinstance(value, uuid.UUID):
                return str(value)
            elif isinstance(value, int):  # в некоторых enum числовые ключи, это не нумерик фильтр!
                return str(value)
            else:
                return value

        def is_in_constant_module(member):
            return member is available_values

        url = f"api/v1/{self.entity}/list"
        response = test_client.get(
            url,
            params={"meta": True},
            headers={"Authorization": f"Bearer {auth_data['access_token']}"},
        )
        filters = {}
        meta = response.json()["meta"]["table_mapping"]
        for column in meta:
            if (values := column.get("available_values")) is not None:
                if not values:
                    ValidationException(detail=f"No values for {column}, please add examples to data.sql")
                filters[column["filter_by"]] = list(values.keys()) + [None]

        fields = self.iread.Meta.fields
        # todo проверку схемы можно делать без запросов к апи в отдельном тесте
        for key, value in fields.items():
            if value.get("is_filterable") is True and "available_values" in value:
                raise ValueError(f"Can't be both is_filterable and available_values {key}")
            elif value.get("is_filterable") is True:  # числовые фильтры в отдельном тесте
                continue
            elif "filter_by" in value:
                column = value["filter_by"]
            elif "available_values" in value:
                column = key
            else:
                continue
            available_values = value["available_values"]
            constant_presents = inspect.getmembers(constants_module, is_in_constant_module)
            # pick values like available_values: constants.name
            # skip available_values: NameEnum.get_info() and CacheV2KV.value
            if constant_presents:
                for pk, constant in value["available_values"].items():
                    # seek for constants {id: value} for example BRAND_AV, skip {value: value} for ex COLOR_AV
                    # multiselect is different logic
                    if pk != constant and "filter_by" not in value and not value.get("is_multiselect", False):
                        raise ValueError(f"Should be filter_by {key} for {pk} {constant}")

        response = test_client.get(
            url,
            params={"filters": json.dumps(filters)},
            headers={"Authorization": f"Bearer {auth_data['access_token']}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_report(self, test_client, auth_data):
        url = f"api/v1/{self.entity}/report"
        response = test_client.get(url, headers={"Authorization": f"Bearer {auth_data['access_token']}"})
        assert response.status_code == 200


class SearchOnMixin:
    @pytest.mark.asyncio
    async def test_list_fts(self, test_client, auth_data):
        url = f"api/v1/{self.entity}/list"
        response = test_client.get(
            url,
            params={
                "search": json.dumps(
                    [
                        "test",
                    ]
                )
            },
            headers={"Authorization": f"Bearer {auth_data['access_token']}"},
        )
        assert response.status_code == 200


class SearchOffMixin:
    @pytest.mark.asyncio
    async def test_list_fts_unavailable(self, test_client, auth_data):
        url = f"api/v1/{self.entity}/list"
        response = test_client.get(
            url,
            params={
                "search": json.dumps(
                    [
                        "test",
                    ]
                )
            },
            headers={"Authorization": f"Bearer {auth_data['access_token']}"},
        )
        assert response.status_code == 422 and response.json()["detail"] == "Search is not available here"


class PeriodOnMixin:
    @pytest.mark.asyncio
    async def test_period_422(self, test_client, auth_data):
        url = f"api/v1/{self.entity}/list"

        response = test_client.get(
            url,
            params={"period": "2004-12-19:2004-12-18"},
            headers={"Authorization": f"Bearer {auth_data['access_token']}"},
        )
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "payload,items_len",
        [
            ("2004-12-19:2004-12-19", 3),
            ("2004-12-19:2004-12-20", 4),
            (json.dumps({"created_at": "2024-05-08:2024-05-08", "updated_at": "2024-06-08:2024-06-08"}), 1),
        ],
    )
    @pytest.mark.asyncio
    async def test_same_period(self, test_client, auth_data, payload, items_len):
        """Тест для фильтрации по датам. Данные тестирования добавлены только для сущности card"""
        url = f"api/v1/{self.entity}/list"
        response = test_client.get(
            url,
            params={"period": payload},
            headers={"Authorization": f"Bearer {auth_data['access_token']}"},
        )
        assert len(response.json()["data"]["items"]) == items_len


class BulkUpdateMixin:
    update_ids = None  # list of 2 or more entity ids in the tests/data.sql

    @pytest.mark.asyncio
    async def test_bulk_update(self, test_client, auth_data):
        if self.update_ids is None:
            raise NotImplementedError("update_ids must be defined")

        if self.update_data is None:
            raise NotImplementedError("update_data must be defined")
        url = f"api/v1/{self.entity}/{'.'.join(self.update_ids)}"

        response = test_client.patch(
            url, json=self.update_data, headers={"Authorization": f"Bearer {auth_data['access_token']}"}
        )
        assert response.status_code == 200

    # @pytest.mark.asyncio
    # async def test_changelog(self, test_client, auth_data):
    #     url = f"api/v1/{self.entity}"
    #     response = test_client.post(url, headers={"Authorization": f"Bearer {auth_data['access_token']}"})
    #     assert response.status_code == 200

    # @pytest.mark.asyncio
    # async def test_crud_bulk(self, test_client, auth_data):

    #     ## Create
    #     url = f"api/v1/{self.entity}"
    #     response = test_client.post(
    #         url, json=[self.create_data], headers={"Authorization": f"Bearer {auth_data['access_token']}"}
    #     )
    #     assert response.status_code == 200
    #     list_id = [id for id in response.json()["data"]]
    #     list_id = list_id.join(".")
    #     logger.info("create test passed")

    #     ## Read
    #     url = f"api/v1/{self.entity}/{list_id}"
    #     response = test_client.get(url, headers={"Authorization": f"Bearer {auth_data['access_token']}"})
    #     assert response.status_code == 200
    #     logger.info("read test passed")

    #     ## Update
    #     response = test_client.patch(
    #         url, json=self.update_data, headers={"Authorization": f"Bearer {auth_data['access_token']}"}
    #     )
    #     assert response.status_code == 200
    #     logger.info("update test passed")

    #     ## Delete
    #     response = test_client.delete(url, headers={"Authorization": f"Bearer {auth_data['access_token']}"})
    #     assert response.status_code == 200
    #     logger.info("delete test passed")
