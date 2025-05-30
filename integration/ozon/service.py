from typing import Any, Optional

import httpx
from integration.ozon.schema import (
    DiscountRequestListResponse,
    DiscountRequestSuccessResponse,
    ProductImportPriceErrorResponse,
    ProductImportPriceResponse,
)
from integration.schema import APIResponse, DefaultErrorResponse
from pydantic import parse_obj_as

from app.common.mock_data_mp_response import (
    action_ozon_product_exit_action,
    actions_ozon_create_from_file,
)
from core.logger import logger
from core.settings import settings


async def fetch_products(
    product_ids: Optional[list[int]] = None,
    vendor_codes: Optional[list[str]] = None,
    skus: Optional[list[int]] = None,
    api_key: str = None,
    client_id: str = None,
) -> dict:
    """
    Fetch product from Ozon API by product id, sku or vendor code.
    Args:
        product_ids: List of product ids.
        vendor_codes: List of vendor codes.
        skus: List of skus.
        api_key: API key for Ozon API.
        client_id: Client id for Ozon API.

    Returns:
        Tuple of (marketplace, product_photos).

    Example response from Ozon API:
    {
      "items": [
        {
          "barcodes": [
            "string"
          ],
          "color_image": [
            "string"
          ],
          "commissions": [
            {
              "delivery_amount": 0,
              "percent": 0,
              "return_amount": 0,
              "sale_schema": "string",
              "value": 0
            }
          ],
          "created_at": "2019-08-24T14:15:22Z",
          "currency_code": "string",
          "description_category_id": 0,
          "discounted_fbo_stocks": 0,
          "errors": [
            {
              "attribute_id": 0,
              "code": "string",
              "field": "string",
              "level": "ERROR_LEVEL_UNSPECIFIED",
              "state": "string",
              "texts": {
                "attribute_name": "string",
                "description": "string",
                "hint_code": "string",
                "message": "string",
                "params": [
                  {
                    "name": "string",
                    "value": "string"
                  }
                ],
                "short_description": "string"
              }
            }
          ],
          "has_discounted_fbo_item": true,
          "id": 0,
          "images": [
            "string"
          ],
          "images360": [
            "string"
          ],
          "is_archived": true,
          "is_autoarchived": true,
          "is_discounted": true,
          "is_kgt": true,
          "is_prepayment_allowed": true,
          "is_super": true,
          "marketing_price": "string",
          "min_price": "string",
          "model_info": {
            "count": 0,
            "model_id": 0
          },
          "name": "string",
          "offer_id": "string",
          "old_price": "string",
          "price": "string",
          "price_indexes": {
            "color_index": "COLOR_INDEX_UNSPECIFIED",
            "external_index_data": {
              "minimal_price": "string",
              "minimal_price_currency": "string",
              "price_index_value": 0
            },
            "ozon_index_data": {
              "minimal_price": "string",
              "minimal_price_currency": "string",
              "price_index_value": 0
            },
            "self_marketplaces_index_data": {
              "minimal_price": "string",
              "minimal_price_currency": "string",
              "price_index_value": 0
            }
          },
          "primary_image": [
            "string"
          ],
          "sources": [
            {
              "created_at": "2019-08-24T14:15:22Z",
              "quant_code": "string",
              "shipment_type": "SHIPMENT_TYPE_UNSPECIFIED",
              "sku": 0,
              "source": "string"
            }
          ],
          "statuses": {
            "is_created": true,
            "moderate_status": "string",
            "status": "string",
            "status_description": "string",
            "status_failed": "string",
            "status_name": "string",
            "status_tooltip": "string",
            "status_updated_at": "2019-08-24T14:15:22Z",
            "validation_status": "string"
          },
          "stocks": {
            "has_stock": true,
            "stocks": [
              {
                "present": 0,
                "reserved": 0,
                "sku": 0,
                "source": "string"
              }
            ]
          },
          "type_id": 0,
          "updated_at": "2019-08-24T14:15:22Z",
          "vat": "string",
          "visibility_details": {
            "has_price": true,
            "has_stock": true
          },
          "volume_weight": 0
        }
      ]
    }
    """
    url = "https://api-seller.ozon.ru/v3/product/info/list"
    headers = {"api-key": api_key, "client-id": str(client_id), "content-type": "application/json"}

    empty_result = {}

    if not product_ids and not vendor_codes:
        logger.warning("At least one of the parameters must be specified.")
        return empty_result

    data = {}
    if skus:
        data["sku"] = skus
    elif vendor_codes:
        data["offer_id"] = vendor_codes
    elif product_ids:
        data["product_id"] = product_ids

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(url, headers=headers, json=data)
        return response.json()
    except Exception as e:
        logger.error(
            f"Error while fetching products: url: {url} data:{data} headers:{headers} response{response.text}"
            f"error: {e}"
        )
        raise e


async def fetch_category(api_key: str = None, client_id: str = None) -> dict:
    """
    Fetch category from Ozon API by category id.
    Args:
        api_key: API key for Ozon API.
        client_id: Client id for Ozon API.

    Returns:
        Category info.

    Example response from Ozon API:
        {
          "result": [
            {
              "description_category_id": 0,
              "category_name": "string",
              "disabled": false,
              "children": [
                {
                  "description_category_id": 0,
                  "category_name": "string",
                  "disabled": false,
                  "children": [
                    {
                      "type_name": "sting",
                      "type_id": 0,
                      "disabled": false,
                      "children": []
                    }
                  ]
                }
              ]
            }
          ]
        }
    """
    url = "https://api-seller.ozon.ru/v1/description-category/tree"

    headers = {"api-key": api_key, "client-id": str(client_id), "content-type": "application/json"}

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.post(url, headers=headers)
    return response.json()


async def upload_final_cost(
    prices: dict[str, list[list[str, Any]]], api_key: str = None, client_id: str = None
) -> APIResponse[ProductImportPriceResponse | ProductImportPriceErrorResponse | DefaultErrorResponse]:
    """
    https://docs.ozon.ru/api/seller/#operation/ProductAPI_ImportProductsPrices
    Args:
        prices: {
            "prices": [
                {
                    "auto_action_enabled": "UNKNOWN",
                    "currency_code": "RUB",
                    "min_price": "800",
                    "offer_id": "",
                    "old_price": "0",
                    "price": "1448",
                    "price_strategy_enabled": "UNKNOWN",
                    "product_id": 1386
                }
            ]
        }
        api_key: API key for Ozon API.
        client_id: Client id for Ozon API.

    Returns:
        Updated info.

    Example response from Ozon API:
        {
            "result": [
                {
                    "product_id": 1386,
                    "offer_id": "PH8865",
                    "updated": true,
                    "errors": [ ]
                }
            ]
        }
    """
    url = "https://api-seller.ozon.ru/v1/product/import/prices"
    headers = {"api-key": api_key, "client-id": str(client_id), "content-type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(url, headers=headers, json=prices)
            logger.info(f"Upload final cost: status code: {response.status_code}, data: {response.text}")

        match response.status_code:
            case 200:
                data = ProductImportPriceResponse.parse_obj(response.json())
                return APIResponse[ProductImportPriceResponse](data=data, status_code=response.status_code)
            case 400 | 403 | 404 | 409 | 500:
                data = ProductImportPriceErrorResponse.parse_obj(response.json())
                return APIResponse[ProductImportPriceErrorResponse](data=data, status_code=response.status_code)
            case _:
                return APIResponse[DefaultErrorResponse](
                    data=DefaultErrorResponse(error=f"Unexpected status code: {response.status_code}"),
                    status_code=response.status_code,
                )
    except Exception as e:
        return APIResponse[DefaultErrorResponse](data=DefaultErrorResponse(error=str(e)), status_code=500)


async def upload_action(keys, items):
    """
    Activate particular products in the action.

    Request example:
    {
      "action_id": 60564,
      "products": [
        {
          "action_price": 356,
          "product_id": 1389,
          "stock": 10
        }
      ]
    }

    Response example:
    {
      "result": {
        "product_ids": [
          1389
        ],
        "rejected": []
      }
    }
    """
    if settings.ENVIRONMENT in ("staging", "production"):
        url = "https://api-seller.ozon.ru/v1/actions/products/activate"
        responses_data = []
        for client_id, api_key in keys.items():
            headers = {"api-key": api_key, "client-id": str(client_id), "content-type": "application/json"}
            if items.get(client_id):
                for action_id, upload_items in items[client_id].items():
                    data_in_mp = {"action_id": action_id, "products": []}
                    if len(upload_items) > 100:
                        for idx, item in enumerate(upload_items):
                            data_in_mp["products"].append(item)
                            if idx % 99 == 0:
                                async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                                    response = await client.post(url, headers=headers, json=data_in_mp)
                                responses_data.append(
                                    data_in_mp | {"status_code": response.status_code, "json": response.json()}
                                )
                                data_in_mp = {"action_id": action_id, "products": []}
                    else:
                        data_in_mp["products"] = upload_items
                        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                            response = await client.post(url, headers=headers, json=data_in_mp)
                        responses_data.append(
                            data_in_mp | {"status_code": response.status_code, "json": response.json()}
                        )
        return responses_data
    else:
        return actions_ozon_create_from_file


async def get_actions(api_key, client_id) -> dict:
    """
    Get Ozon actions.
    https://docs.ozon.ru/api/seller/#operation/Promos

    Args:
        api_key: API key for Ozon API.
        client_id: Client id for Ozon API.

    Returns:
        Dict[str, Any]: The response from the Ozon API containing the list of actions.

    Example response from Ozon API:
    {
      "result": [
        {
          "id": 71342,
          "title": "test voucher #2",
          "date_start": "2021-11-22T09:46:38Z",
          "date_end": "2021-11-30T20:59:59Z",
          "potential_products_count": 0,
          "is_participating": true,
          "participating_products_count": 5,
          "description": "",
          "action_type": "DISCOUNT",
          "banned_products_count": 0,
          "with_targeting": false,
          "discount_type": "UNKNOWN",
          "discount_value": 0,
          "order_amount": 0,
          "freeze_date": "",
          "is_voucher_action": true
        }
      ]
    }

    """

    url = "https://api-seller.ozon.ru/v1/actions"
    headers = {"api-key": api_key, "client-id": str(client_id), "content-type": "application/json"}
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"{response.status_code}, {response.json()}, {client_id}")
        return response.json()


async def get_all_products_in_action(api_key, client_id, limit, ofset, action_id):
    """
    Get products in the action.
    https://docs.ozon.ru/api/seller/#operation/PromosProducts

    Args:
        api_key: API key for Ozon API.
        client_id: Client id for Ozon API.
        action_id: Action id.
        limit: Limit of products.
        ofset: Offset of products.

    Returns:
        Dict[str, Any]: The response from the Ozon API containing the list of products in the action.

    Example response from Ozon API:
    {
      "result": {
        "products": [
          {
            "id": 1383,
            "price": 5503,
            "action_price": 621,
            "max_action_price": 3712.1,
            "add_mode": "MANUAL",
            "stock": 0,
            "min_stock": 0
          }
        ],
        "total": 1
      }
    }
    """
    data = {"action_id": action_id, "limit": limit, "offset": ofset}
    url = "https://api-seller.ozon.ru/v1/actions/products"
    headers = {"api-key": api_key, "client-id": str(client_id), "content-type": "application/json"}
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.post(url, headers=headers, json=data)
        if response.status_code != 200:
            logger.error(f"{response.status_code}, {response.json()}, {client_id}")
        return response.json(), response.status_code


async def delete_product_in_action(keys, items):
    """
    Deactivate particular products in the action.
    https://docs.ozon.ru/api/seller/#operation/PromosProductsDeactivate

    Args:
        keys: {
            <client_id>: <api_key>
        }
        items: {
            <client_id>: {
                <action_id>: [
                    <product_id>
                ]
            }
        }

    Returns:
        List[Dict[str, Any]]: The response from the Ozon API containing the result of the deactivation process.

    Example request:
    {
      "action_id": 66011,
      "product_ids": [
        14975
      ]
    }

    Example response from Ozon API:
    {
      "result": {
        "product_ids": [
          14975
        ],
        "rejected": []
      }
    }
    """

    if settings.ENVIRONMENT in ("staging", "production"):
        url = "https://api-seller.ozon.ru/v1/actions/products/deactivate"
        responses_data = []
        for client_id, api_key in keys.items():
            headers = {"api-key": api_key, "client-id": str(client_id), "content-type": "application/json"}
            if items.get(client_id):
                for action_id, upload_items in items[client_id].items():
                    data_in_mp = {"action_id": action_id, "product_ids": []}
                    if len(upload_items) > 100:
                        for idx, item in enumerate(upload_items):
                            data_in_mp["product_ids"].append(item)
                            if idx % 99 == 0:
                                async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                                    response = await client.post(url, headers=headers, json=data_in_mp)
                                responses_data.append(
                                    data_in_mp | {"status_code": response.status_code, "json": response.json()}
                                )
                                data_in_mp = {"action_id": action_id, "product_ids": []}
                    else:
                        data_in_mp["product_ids"] = upload_items
                        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                            response = await client.post(url, headers=headers, json=data_in_mp)
                        responses_data.append(
                            data_in_mp | {"status_code": response.status_code, "json": response.json()}
                        )
        return responses_data
    else:
        return action_ozon_product_exit_action


############################################################################################################


async def discount_request_list(
    api_key: str,
    client_id: str,
    page: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
) -> list[DiscountRequestListResponse]:
    """
    Fetch the list of discount tasks from Ozon API.
    Documentation: https://docs.ozon.ru/api/seller/en/?utm_source=tg_seller_bot#operation/promos_task_list

    Args:
        api_key (str): API key for Ozon API.
        client_id (str): Client id for Ozon API.
        status (str, optional): Status of the discount task. Available statuses: "NEW" "SEEN" "APPROVED"
         "PARTLY_APPROVED" "DECLINED" "AUTO_DECLINED" "DECLINED_BY_USER" "COUPON" "PURCHASED".
        page (int, optional): Page number for pagination. Defaults to 1.
        limit (int, optional): Maximum number of items per page. Defaults to 100.

    Returns:
        Dict[str, Any]: The response from the Ozon API containing the list of discount tasks.

    Raises:
        httpx.HTTPStatusError: If the API request fails.

    Example response structure:
    {
        "result": [
            {
                "id": 0,
                "created_at": "2019-08-24T14:15:22Z",
                "end_at": "2019-08-24T14:15:22Z",
                "edited_till": "2019-08-24T14:15:22Z",
                "status": "string",
                "customer_name": "string",
                "sku": 0,
                "user_comment": "string",
                "seller_comment": "string",
                "requested_price": 0,
                "approved_price": 0,
                "original_price": 0,
                "discount": 0,
                "discount_percent": 0,
                "base_price": 0,
                "min_auto_price": 0,
                "prev_task_id": 0,
                "is_damaged": true,
                "moderated_at": "2019-08-24T14:15:22Z",
                "approved_discount": 0,
                "approved_discount_percent": 0,
                "is_purchased": true,
                "is_auto_moderated": true,
                "offer_id": "string",
                "email": "string",
                "last_name": "string",
                "first_name": "string",
                "patronymic": "string",
                "approved_quantity_min": 0,
                "approved_quantity_max": 0,
                "requested_quantity_min": 0,
                "requested_quantity_max": 0,
                "requested_price_with_fee": 0,
                "approved_price_with_fee": 0,
                "approved_price_fee_percent": 0
            }
        ]
    }
    """
    url = "https://api-seller.ozon.ru/v1/actions/discounts-task/list"
    headers = {"api-key": api_key, "client-id": str(client_id), "Content-Type": "application/json"}
    data = {"page": page, "limit": limit}

    if status:
        data["status"] = status

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.post(url, headers=headers, json=data)
        response_data = response.json()

    return parse_obj_as(list[DiscountRequestListResponse], response_data.get("result", []))


async def discount_request_approve(api_key: str, client_id: str, tasks: list[dict]) -> DiscountRequestSuccessResponse:
    """
    Approve discount tasks in Ozon API.
    Documentation https://docs.ozon.ru/api/seller/en/?utm_source=tg_seller_bot#operation/promos_task_approve

    This method can approve tasks with statuses 'NEW' and 'SEEN'.

    Args:
        api_key (str): API key for Ozon API.
        client_id (str): Client id for Ozon API.
        tasks (List[Dict[str, Any]]): List of tasks to approve. Each task is a dictionary with the following keys:
            - id (int): Task identifier.
            - approved_price (float): Approved price.
            - seller_comment (str): Seller's comment on the task.
            - approved_quantity_min (int): Approved minimum quantity of items.
            - approved_quantity_max (int): Approved maximum quantity of items.

    Returns:
        Dict[str, Any]: The response from the Ozon API containing the result of the approval process.

    Raises:
        httpx.HTTPStatusError: If the API request fails.

    Example usage:
        tasks = [
            {
                "id": 123456,
                "approved_price": 999.99,
                "seller_comment": "Approved with discount",
                "approved_quantity_min": 1,
                "approved_quantity_max": 10
            }
        ]
        response = await approve_discounts_task(api_key, client_id, tasks)

    Example response structure:
    {
        "result": {
            "fail_details": [
                {
                    "task_id": 0,
                    "error_for_user": "string"
                }
            ],
            "success_count": 0,
            "fail_count": 0
        }
    }
    """
    url = "https://api-seller.ozon.ru/v1/actions/discounts-task/approve"
    headers = {"api-key": api_key, "client-id": str(client_id), "Content-Type": "application/json"}
    data = {"tasks": tasks}
    logger.debug(f"Approving discount tasks: {data}")
    logger.debug(f"curl -X POST '{url}' -H '{headers}' -d '{data}'")

    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
        response = await client.post(url, headers=headers, json=data)
        logger.debug(f"Response: {response.text}")
        response_data = response.json()
        response_data = response_data.get("result", {})
        response_data["status_code"] = response.status_code

    return DiscountRequestSuccessResponse.parse_obj(response_data)


async def discount_request_decline(api_key: str, client_id: str, tasks: list[dict]) -> DiscountRequestSuccessResponse:
    """
    Approve discount tasks in Ozon API.
    Documentation https://docs.ozon.ru/api/seller/en/?utm_source=tg_seller_bot#operation/promos_task_decline

    This method can decline tasks with statuses 'NEW' and 'SEEN'.

    Args:
        api_key (str): API key for Ozon API.
        client_id (str): Client id for Ozon API.
        tasks (List[Dict[str, Any]]): List of tasks to approve. Each task is a dictionary with the following keys:
            - id (int): Task identifier.
            - seller_comment (str): Seller's comment on the task.

    Returns:
        Dict[str, Any]: The response from the Ozon API containing the result of the approval process.

    Raises:
        httpx.HTTPStatusError: If the API request fails.

    Example usage:
        tasks = [
            {
                "id": 123456,
                "seller_comment": "Approved with discount"
            }
        ]
        response = await approve_discounts_task(api_key, client_id, tasks)

    Example response structure:
    {
        "result": {
            "fail_details": [
                {
                    "task_id": 0,
                    "error_for_user": "string"
                }
            ],
            "success_count": 0,
            "fail_count": 0
        }
    }
    """
    url = "https://api-seller.ozon.ru/v1/actions/discounts-task/decline"
    headers = {"api-key": api_key, "client-id": str(client_id), "Content-Type": "application/json"}
    data = {"tasks": tasks}
    logger.debug(f"Approving discount tasks: {data}")
    logger.debug(f"curl -X POST '{url}' -H '{headers}' -d '{data}'")

    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
        response = await client.post(url, headers=headers, json=data)
        logger.debug(f"Response: {response.text}")
        response_data = response.json()
        response_data = response_data.get("result", {})
        response_data["status_code"] = response.status_code

    return DiscountRequestSuccessResponse.parse_obj(response_data)
