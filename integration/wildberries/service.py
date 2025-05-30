from typing import AsyncGenerator, Optional

import httpx
from integration.schema import APIResponse, DefaultErrorResponse
from integration.wildberries.schema import (
    UploadTaskPriceErrorResponse,
    UploadTaskPriceResponse,
)

from core.logger import logger


async def fetch_products(search_code: str, auth_token: str = None) -> (str, list[dict]):
    """
    Fetch product from Wildberries API by search code (it could be either nmID(sku) or skus(barcode)).

    Args:
        search_code: Search code (it could be either nmID(sku) or skus(barcode)).
        auth_token: Authorization token for Wildberries API.

    Returns:
        Tuple of (marketplace, card_id, product_photos).

    Example response from Wildberries API:
    {
      "cards": [
        {
          "nmID": 165427612,
          "imtID": 151640770,
          "nmUUID": "018c0914-7935-76dc-b814-b80fb8ddc60c",
          "subjectID": 832,
          "subjectName": "Фруктовницы",
          "vendorCode": "Levina\\NG-001943черный",
          "brand": "Jerta",
          "title": "Фруктовница металлическая Корзина для фруктов Ваза конфет",
          "description": "Фруктовница - идеальное сочетание функциональности, стиля и качества. Наша металлическая ваза для фруктов предлагает вам прекрасное решение для оформления и хранения свежих фруктов. Сочетание металлической подставки и корзинки обеспечивает прочность и надежность, позволяя вашим фруктам оставаться свежими и легко доступными. Фруктница станет прекрасным дополнением к вашей кухонной посуде, придавая ей неповторимый шарм, украшая любой праздничный стол. В нее поместятся до 2 килограмм фруктов и овощей, орехов и сухофруктов. Ее стильный плетеный дизайн и элегантные линии позволят вам создать идеальную фруктовую композицию, которая притянет взгляды и добавит изысканности в ваш интерьер. Она станет прекрасным элементом декора для гостиной и отличным набором сервировочной посуды для отдыха. Наша фруктовая чаша не только является идеальным аксессуаром для вашей кухни, но также может служить удобным органайзером для конфет, овощей и других продуктов. Благодаря своей вместительности и функциональности, корзина в стиле лофт поможет вам организовать пространство и подчеркнет ваш стиль. Не упустите возможность добавить шарма и изысканности в свою кухню с помощью фруктовницы. Такая емкость для хранения фруктов и овощей будет полезным подарком для мужа и жены, женщины и мужчины, подруги и друга , бабушки и дедушки, любимого и любимой, на Новый год, 23 февраля (День Защитника Отечества), 8 марта (Женский день), 14 февраля (День Святого Валентина), День Рождения.",
          "video": "https://video.wildberries.ru/video/new/165420000/165427612.mp4",
          "photos": [
            {
              "516x288": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/516x288/1.jpg",
              "big": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/big/1.jpg",
              "small": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/small/1.jpg"
            },
            {
              "516x288": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/516x288/2.jpg",
              "big": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/big/2.jpg",
              "small": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/small/2.jpg"
            },
            {
              "516x288": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/516x288/3.jpg",
              "big": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/big/3.jpg",
              "small": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/small/3.jpg"
            },
            {
              "516x288": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/516x288/4.jpg",
              "big": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/big/4.jpg",
              "small": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/small/4.jpg"
            },
            {
              "516x288": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/516x288/5.jpg",
              "big": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/big/5.jpg",
              "small": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/small/5.jpg"
            },
            {
              "516x288": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/516x288/6.jpg",
              "big": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/big/6.jpg",
              "small": "https://basket-11.wbbasket.ru/vol1654/part165427/165427612/images/small/6.jpg"
            }
          ],
          "dimensions": {
            "length": 27,
            "width": 27,
            "height": 8
          },
          "characteristics": [
            {
              "id": 12,
              "name": "Рисунок",
              "value": [
                "плетеная"
              ]
            },
            {
              "id": 16685,
              "name": "Материал посуды",
              "value": [
                "Металл",
                "Нержавеющая сталь",
                "Железо"
              ]
            },
            {
              "id": 90602,
              "name": "Диаметр предмета",
              "value": 25
            },
            {
              "id": 58813,
              "name": "Назначение посуды",
              "value": [
                "Для дома",
                "Товары для пикника",
                "Декоративная посуда"
              ]
            },
            {
              "id": 72443,
              "name": "Хрупкость",
              "value": [
                "Не хрупкое",
                "Надежно упаковано"
              ]
            },
            {
              "id": 88952,
              "name": "Вес товара с упаковкой (г)",
              "value": 171
            },
            {
              "id": 14177449,
              "name": "Цвет",
              "value": [
                "черный"
              ]
            },
            {
              "id": 14177451,
              "name": "Страна производства",
              "value": [
                "Китай"
              ]
            },
            {
              "id": 378533,
              "name": "Комплектация",
              "value": [
                "Фруктовница металлическая - 1 шт."
              ]
            },
            {
              "id": 23796,
              "name": "Назначение",
              "value": [
                "Кухонная фруктовая корзинка",
                "Конфетница для кухни, лофт",
                "Для дачи и офиса"
              ]
            },
            {
              "id": 14970,
              "name": "Количество ярусов",
              "value": [
                "1 шт."
              ]
            }
          ],
          "sizes": [
            {
              "chrtID": 275457111,
              "techSize": "0",
              "wbSize": "",
              "skus": [
                "2038037040971"
              ]
            }
          ],
          "createdAt": "2023-06-15T12:52:26.072128Z",
          "updatedAt": "2023-08-22T14:30:03.033946Z"
        }
      ],
      "cursor": {
        "updatedAt": "2023-08-22T14:30:03.033946Z",
        "nmID": 165427612,
        "total": 1
      }
    }
    """
    empty_list = {}

    if not search_code:
        logger.warning("At search code must be specified.")
        return empty_list

    url = "https://content-api.wildberries.ru/content/v2/get/cards/list?locale=ru"
    headers = {"Authorization": auth_token}
    data = {"settings": {"cursor": {"limit": 1}, "filter": {"withPhoto": -1, "textSearch": str(search_code)}}}

    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
        response = await client.post(url, headers=headers, json=data)

    logger.info(f"Response text: {response.text}")
    return response.json()


async def fetch_all_account_products(auth_token: str) -> AsyncGenerator[dict, None]:
    """POST https://suppliers-api.wildberries.ru/content/v2/get/cards/list?locale=ru
    Authorization: eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjMxMDI1djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTcxNjg2MjY1MiwiaWQiOiIyZWE1ODkyMS02ZDJhLTRkNTktYWVmOC0zYjJjM2RhZDI0ZWUiLCJpaWQiOjgzMzgxOTk5LCJvaWQiOjczMTUyMiwicyI6NTEwLCJzaWQiOiI1ZTUzNTY2My05MWM5LTQ4MjYtOTgwNi05OTA0NmVhZDk3YjYiLCJ1aWQiOjgzMzgxOTk5fQ.f_aHWdsmcVxKEw4lv0LWyzYiQAAMqa7Xw5XF6_FkMu3PUuOeOs_cnpRjQqM7hNbLVhRXieXRjVD7UF0-vcRr8A

    {
      "settings": {
        "cursor": {
          "limit": 100,
          "updatedAt": "2024-03-26T07:08:33.842741Z",
          "nmID": 105989332
        },
        "filter": {
          "withPhoto": -1
        }
      }
    }
    """
    iteration_number = 0
    url = "https://content-api.wildberries.ru/content/v2/get/cards/list?locale=ru"
    headers = {"Authorization": auth_token}
    max_items = 100
    settings = {"settings": {"cursor": {"limit": max_items}, "filter": {"withPhoto": -1}}}
    continue_fetch = True

    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
        while continue_fetch:
            response = await client.post(url, headers=headers, json=settings)
            logger.info(f"[{iteration_number}]### -> Response[{response.status_code}] text: {response.text[:100]}")
            response = response.json()
            yield response
            if not response.get("cursor") or response["cursor"]["total"] < max_items:
                continue_fetch = False
            else:
                settings.update(
                    {
                        "settings": {
                            "cursor": {
                                "limit": max_items,
                                "updatedAt": response["cursor"]["updatedAt"],
                                "nmID": response["cursor"]["nmID"],
                            },
                            "filter": {"withPhoto": -1},
                        }
                    }
                )


async def fetch_all_categories(auth_token: str = None, offset: int = 0, limit: int = 1000) -> dict:
    """
    Fetch all categories from Wildberries API.

    Args:
        auth_token: Authorization token for Wildberries API.
        offset: Offset.
        limit: Limit.


    Returns:
        All categories.

    Example response from Wildberries API:
        {
          "data": [
            {
              "subjectID": 832,
              "parentID": 1590,
              "subjectName": "Фруктовницы",
              "parentName": "Посуда и инвентарь",
              "isVisible": true
            }
            ...
          ],
          "error": false,
          "errorText": "",
          "additionalErrors": null
        }
    """

    url = f"https://content-api.wildberries.ru/content/v2/object/all?limit={limit}&locale=ru&offset={offset}"
    headers = {"Authorization": auth_token}

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            response = await client.get(url, headers=headers)

        return response.json()
    except Exception as e:
        logger.error(
            f"Error while fetching products: url: {url} headers:{headers} response{response.text}" f"error: {e}"
        )
        raise e


async def upload_final_cost(
    auth_token,
    items: dict[str, list[dict[str, int]]],
) -> APIResponse[UploadTaskPriceResponse | UploadTaskPriceErrorResponse | DefaultErrorResponse]:
    """
    Загрузка цен. За раз можно загрузить не более 1000 номенклатур.

    Args:
        auth_token: Authorization token for Wildberries API.
        {
          data: [
                      {
                          "nmId": 1234567,
                          "price": 1000   #без копеек,
                          "discount": 30
                      },
                      {
                          str:int,
                          str:int,
                          str:int
                      }
                ]
        }
    """
    url = "https://discounts-prices-api.wildberries.ru/api/v2/upload/task"
    headers = {"Authorization": auth_token}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(url, headers=headers, json=items)
            logger.info(f"Upload final cost: status code: {response.status_code}, data: {response.text}")

        match response.status_code:
            case 200 | 208 | 400 | 422:
                data = UploadTaskPriceResponse.parse_obj(response.json())
                return APIResponse[UploadTaskPriceResponse](data=data, status_code=response.status_code)
            case 401 | 429:
                data = UploadTaskPriceErrorResponse.parse_obj(response.json())
                return APIResponse[UploadTaskPriceErrorResponse](data=data, status_code=response.status_code)
            case _:
                return APIResponse[DefaultErrorResponse](
                    status_code=response.status_code,
                    data=DefaultErrorResponse(error=response.text),
                )
    except Exception as e:
        return APIResponse[DefaultErrorResponse](
            data=DefaultErrorResponse(error=str(e)), status_code=response.status_code
        )


async def upload_final_cost_size(
    auth_token, items: dict[str, list[dict[str, int]]]
) -> APIResponse[UploadTaskPriceResponse | UploadTaskPriceErrorResponse | DefaultErrorResponse]:
    """
    Загрузка цен. За раз можно загрузить не более 1000 номенклатур.

    Args:
        auth_token: Authorization token for Wildberries API.
        {
          data: [
                      {
                          "nmID": 123,
                          "sizeID": 98989887,
                          "price": 999  #без копеек
                      },
                      {
                          str:int,
                          str:int,
                          str:int,
                      }
                ]
        }
    """
    url = "https://discounts-prices-api.wildberries.ru/api/v2/upload/task/size"
    headers = {"Authorization": auth_token}

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(url, headers=headers, json=items)
            logger.info(f"Upload final cost: status code: {response.status_code}, data: {response.text}")

        match response.status_code:
            case 200 | 208 | 400 | 422:
                data = UploadTaskPriceResponse.parse_obj(response.json())
                return APIResponse[UploadTaskPriceResponse](data=data, status_code=response.status_code)
            case 401 | 429:
                data = UploadTaskPriceErrorResponse.parse_obj(response.json())
                return APIResponse[UploadTaskPriceErrorResponse](data=data, status_code=response.status_code)
            case _:
                return APIResponse[DefaultErrorResponse](
                    status_code=response.status_code,
                    data=DefaultErrorResponse(error=response.text),
                )
    except Exception as e:
        return APIResponse[DefaultErrorResponse](
            data=DefaultErrorResponse(error=str(e)), status_code=response.status_code
        )


async def fetch_filter_goods(nm_id: int, auth_token: str) -> Optional[dict]:
    """
    Fetch filter goods from Wildberries API by product id.

    Args:
        nm_id: product id.
        auth_token: Authorization token for Wildberries API.

    Returns:
        Filter goods.

    Example response from Wildberries API:
        GET http://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter?filterNmID=142668062&limit=1
        {
          "data": {
            "listGoods": [
              {
                "nmID": 142668062,
                "vendorCode": "Kharchenkov\\G1072070фуксия",
                "sizes": [
                  {
                    "sizeID": 241108205,
                    "price": 5329,
                    "discountedPrice": 2398.05,
                    "techSizeName": "40"
                  },
                  {
                    "sizeID": 241108206,
                    "price": 5329,
                    "discountedPrice": 2398.05,
                    "techSizeName": "42"
                  },
                  {
                    "sizeID": 241108207,
                    "price": 5329,
                    "discountedPrice": 2398.05,
                    "techSizeName": "44"
                  },
                  {
                    "sizeID": 241108208,
                    "price": 5329,
                    "discountedPrice": 2398.05,
                    "techSizeName": "46"
                  },
                  {
                    "sizeID": 241108209,
                    "price": 5329,
                    "discountedPrice": 2398.05,
                    "techSizeName": "48"
                  },
                  {
                    "sizeID": 241108210,
                    "price": 5329,
                    "discountedPrice": 2398.05,
                    "techSizeName": "50"
                  },
                  {
                    "sizeID": 241108211,
                    "price": 5329,
                    "discountedPrice": 2398.05,
                    "techSizeName": "52"
                  },
                  {
                    "sizeID": 241108212,
                    "price": 5329,
                    "discountedPrice": 2398.05,
                    "techSizeName": "54"
                  },
                  {
                    "sizeID": 303308415,
                    "price": 5329,
                    "discountedPrice": 2398.05,
                    "techSizeName": "56"
                  }
                ],
                "currencyIsoCode4217": "RUB",
                "discount": 55,
                "editableSizePrice": false
              }
            ]
          },
          "error": false,
          "errorText": ""
        }
    """
    url = f"https://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter?limit=1&filterNmID={nm_id}"
    headers = {"Authorization": auth_token}

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.get(url, headers=headers)

    results = response.json()
    if results.get("error"):
        logger.error(f"Error while fetching filter goods from Wildberries API: {results.get('errorText')}")
        return

    return results.get("data", {}).get("listGoods")


async def fetch_all_blocked_products(auth_token: str) -> dict:
    """
    Fetch all blocked product cards.

    NOTE: Maximum of 1 request per 10 seconds per one seller's account

    Args:
        auth_token: Authorization token for Wildberries API.

    Returns:
        Blocked product cards.

    Example of response from Wildberries API:
    {
      "report": [
        {
          "brand": "Тест22",
          "nmId": 82722944,
          "title": "Гуминовые кислоты - биоактивный противовирусный комплекс на",
          "vendorCode": "пкdeир76",
          "reason": "Контактные данные Продавца и ссылки на иные сайты/группы/сообщества на фотографиях Товара"
        }
      ]
    }
    """
    url = "https://seller-analytics-api.wildberries.ru/api/v1/analytics/banned-products/blocked"
    headers = {"Authorization": auth_token}

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.get(url, headers=headers)

    results = response.json()

    return results


async def fetch_all_hidden_products(auth_token: str) -> dict:
    """
    Fetch all hidden product cards from the catalog.

    NOTE: Maximum of 1 request per 10 seconds per one seller's account

    Args:
        auth_token: Authorization token for Wildberries API.

    Returns:
        Blocked product cards.

    Example of response from Wildberries API:
    {
      "report": [
        {
          "brand": "Трикотаж",
          "nmId": 166658151,
          "title": "ВАЗ",
          "vendorCode": "DP02/черный",
          "nmRating": 3.1
        }
      ]
    }
    """
    url = "https://seller-analytics-api.wildberries.ru/api/v1/analytics/banned-products/shadowed"
    headers = {"Authorization": auth_token}

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.get(url, headers=headers)

    results = response.json()

    return results


async def fetch_all_archived_products(auth_token: str) -> AsyncGenerator[dict, None]:
    """
    Fetch all archived product cards from the catalog.

    Args:
        auth_token: Authorization token for Wildberries API.

    Returns:
        Archived product cards

    Example of response from Wildberries API:
    {
      "cards": [
        {
          "nmID": 185719044,
          "vendorCode": "wb17026gin",
          "subjectID": 520,
          "subjectName": "Колонки",
          "photos": [
            {
              "big": "https://basket-12.wbbasket.ru/vol1857/part185719/185719044/images/big/1.webp",
              "c246x328": "https://basket-12.wbbasket.ru/vol1857/part185719/185719044/images/c246x328/1.webp",
              "c516x688": "https://basket-12.wbbasket.ru/vol1857/part185719/185719044/images/c516x688/1.webp",
              "hq": "https://basket-12.wbbasket.ru/vol1857/part185719/185719044/images/hq/1.webp",
              "square": "https://basket-12.wbbasket.ru/vol1857/part185719/185719044/images/square/1.webp",
              "tm": "https://basket-12.wbbasket.ru/vol1857/part185719/185719044/images/tm/1.webp"
            }
            ...
          ],
          "sizes": [
            {
              "chrtID": 305288387,
              "techSize": "0",
              "wbSize": "",
              "skus": [
                "2038876149132"
              ]
            }
          ],
          "dimensions": {
            "width": 8,
            "height": 19,
            "length": 19,
            "isValid": true
          },
          "characteristics": [
            {
              "id": 65667,
              "name": "Максимальная воспроизводимая частота",
              "value": 20000
            }
            ...
            {
              "id": 14177449,
              "name": "Цвет",
              "value": [
                "синий"
              ]
            }
            ...
          ],
          "createdAt": "2023-10-30T14:36:36.296951Z",
          "trashedAt": "2024-07-31T12:11:24.493004Z"
        },
        {
          "nmID": 188367183,
          "vendorCode": "wb3wfsben7",
          "subjectID": 520,
          "subjectName": "Колонки",
          "photos": [
            {
              "big": "https://basket-12.wbbasket.ru/vol1883/part188367/188367183/images/big/1.webp",
              "c246x328": "https://basket-12.wbbasket.ru/vol1883/part188367/188367183/images/c246x328/1.webp",
              "c516x688": "https://basket-12.wbbasket.ru/vol1883/part188367/188367183/images/c516x688/1.webp",
              "hq": "https://basket-12.wbbasket.ru/vol1883/part188367/188367183/images/hq/1.webp",
              "square": "https://basket-12.wbbasket.ru/vol1883/part188367/188367183/images/square/1.webp",
              "tm": "https://basket-12.wbbasket.ru/vol1883/part188367/188367183/images/tm/1.webp"
            }
            ...
          ],
          "video": "https://videonme-basket-06.wbbasket.ru/vol63/part18836/188367183/hls/1440p/index.m3u8",
          "sizes": [
            {
              "chrtID": 308546191,
              "techSize": "0",
              "wbSize": "",
              "skus": [
                "2038936760017"
              ]
            }
          ],
          "dimensions": {
            "width": 8,
            "height": 19,
            "length": 19,
            "isValid": true
          },
          "characteristics": [
            {
              "id": 84844,
              "name": "Совместимые ОС",
              "value": [
                "iOS",
                "Mac OS , Windows",
                "Android"
              ]
            }
            ...
          ],
          "createdAt": "2023-11-08T14:00:37.362678Z",
          "trashedAt": "2024-07-31T12:11:18.181916Z"
        }
      ],
      "cursor": {
        "trashedAt": "2024-07-31T12:11:18.181916Z",
        "nmID": 188367183,
        "total": 2
      }
    }
    """
    iteration_number = 0
    url = "https://content-api.wildberries.ru/content/v2/get/cards/trash?locale=ru"
    headers = {"Authorization": auth_token}
    max_items = 100
    settings = {"settings": {"cursor": {"limit": max_items}}}
    continue_fetch = True

    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
        while continue_fetch:
            response = await client.post(url, headers=headers, json=settings)
            logger.info(f"[{iteration_number}]### -> Response[{response.status_code}] text: {response.text[:100]}")
            response = response.json()
            yield response
            if not response.get("cursor") or response["cursor"]["total"] < max_items:
                continue_fetch = False
            else:
                settings.update(
                    {
                        "settings": {
                            "cursor": {
                                "limit": max_items,
                                "trashedAt": response["cursor"]["trashedAt"],
                                "nmID": response["cursor"]["nmID"],
                            }
                        }
                    }
                )
