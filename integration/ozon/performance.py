import datetime as dt
from typing import Optional
from uuid import UUID

import httpx
from integration.postgres.utils import SQLAdv, job_sql_executor


TOKEN_URL = "https://api-performance.ozon.ru/api/client/token"

ACCOUNT_QUERY = """
                Select
                    id,
                    ozon_performance_client_id,
                    ozon_performance_client_secret
                from
                    core.account
                where
                    account.ozon_performance_client_id is not NULL"""


class PerformanceAuthorizer:
    def __init__(self):
        self.accounts: Optional[dict] = None
        self.api_bearers: dict = {}
        self.token_url: str = TOKEN_URL

    async def get_accounts(self):
        if self.accounts is None:
            accounts_query = await job_sql_executor(ACCOUNT_QUERY, adv=SQLAdv.fetchall)
            self.accounts = {
                row[0]: {
                    "client_id": row[1],
                    "client_secret": row[2],
                }
                for row in accounts_query
            }
        return self.accounts

    async def get_auth_token(self, account_title):
        accounts = await self.get_accounts()
        if not isinstance(account_title, UUID):
            account_title = UUID(account_title)
        client_id = accounts[account_title]["client_id"]
        client_secret = accounts[account_title]["client_secret"]
        token, expires_at = await self.token_request(client_id, client_secret)
        return token, expires_at

    async def token_request(self, client_id, client_secret):
        transport = httpx.AsyncHTTPTransport(retries=2)
        body = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0), transport=transport) as client:
            request = await client.post(TOKEN_URL, json=body)
            # todo валидатор ответа, логгер
            response_json = request.json()
        token = response_json["access_token"]
        expires_at = dt.datetime.now(tz=dt.UTC) + dt.timedelta(seconds=response_json["expires_in"])
        return token, expires_at

    async def get_bearers(self, account_title):
        if self.api_bearers.get(account_title, {}).get("token") is None or self.api_bearers.get(account_title, {}).get(
            "expires_at"
        ) < dt.datetime.now(tz=dt.timezone.utc):
            token, expires_at = await self.get_auth_token(account_title)
            self.api_bearers[account_title] = {"token": token, "expires_at": expires_at}

        return self.api_bearers[account_title]["token"]
