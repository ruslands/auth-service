import urllib.parse

import httpx

from core.settings import settings


async def get_yandex_images(image_url: str) -> dict:
    assert settings.SERPAPI_API_KEY, "Serpapi api key is not set"

    sites = urllib.parse.quote(
        "wildberries.ru,ozon.ru,market.yandex.ru,wildberries.by,ozon.by,ozon.kz,ozon.com,"
        "megamarket.ru,kazanexpress.ru"
    )
    image_url = urllib.parse.quote(image_url)

    url = (
        f"https://serpapi.com/search.json?engine=yandex_images&site={sites}&url={image_url}"
        f"&api_key={settings.SERPAPI_API_KEY}"
    )

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        response = await client.get(url)

    return response.json()
