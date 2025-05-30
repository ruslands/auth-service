import datetime as dt

import httpx

from core.exceptions import BadRequestException
from core.logger import logger
from core.settings import settings


DAG_RUN_FIELDS = ("state", "execution_date")


def check_response(response):
    if response.status_code != 200:
        error = response.json()
        logger.error(f"response status code {response.status_code}: {response.request.url}: {response.text}")
        raise BadRequestException(detail=f'{error.get("status")} {error.get("detail")} {error.get("type")}')
    return response.json()


async def get_httpx_client_settings():
    transport = httpx.AsyncHTTPTransport(retries=2)
    auth = httpx.BasicAuth(username=settings.AIRFLOW["USER"], password=settings.AIRFLOW["PASSWORD"])
    return transport, auth


async def get_dag_list(client: httpx.AsyncClient):
    url = f"{settings.AIRFLOW['URL']}/dags"
    response = await client.get(url)
    return response.json()


async def get_dag_by_id(client: httpx.AsyncClient, dag_id: str):
    url = f"{settings.AIRFLOW['URL']}/dags/{dag_id}"
    response = await client.get(url)
    return check_response(response)


async def get_dagrun_by_dag_id(client: httpx.AsyncClient, dag_id: str):
    url = f"{settings.AIRFLOW['URL']}/dags/{dag_id}/dagRuns"
    body = {
        "limit": 1,
        "order_by": "-execution_date",  # start with minus means reverse order
        "fields": [
            "state",
            "execution_date",
            "dag_id",
        ],
    }
    response = await client.get(url, params=body)
    return check_response(response)


async def get_dagruns(client: httpx.AsyncClient):
    """Get runs since yesterday, max 10000 records

    Slow, heavy request.
    If last execution time are not needed, then we can skip this step.
    """
    url = f"{settings.AIRFLOW['URL']}/dags/~/dagRuns/list"
    yesterday = dt.datetime.now(dt.UTC) - dt.timedelta(days=1)
    body = {
        "page_limit": 10000,
        "order_by": "-execution_date",
        "execution_date_gte": yesterday.isoformat(),
        "states": ["success", "failed"],
    }
    response = await client.post(url, json=body)
    return check_response(response)


def filler_last_dagrun(dagruns):
    """Dagruns ordered by execution_date in request."""
    last_runs = {}

    for run in dagruns:
        if run["dag_id"] not in last_runs:
            last_runs[run["dag_id"]] = {key: run[key] for key in DAG_RUN_FIELDS}
    return last_runs


async def get_list():
    transport, auth = await get_httpx_client_settings()
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0), transport=transport, auth=auth) as client:
        dags_response = await get_dag_list(client)
        dags = dags_response["dags"]
        dagruns_response = await get_dagruns(client)
        dagruns = dagruns_response["dag_runs"]

    last_runs = filler_last_dagrun(dagruns)
    for dag in dags:
        dag.update(last_runs.get(dag["dag_id"], {}))
    return dags


async def get_by_id(ids):
    dags = []
    transport, auth = await get_httpx_client_settings()
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0), transport=transport, auth=auth) as client:
        for dag_id in ids:
            dag = await get_dag_by_id(client, dag_id)
            dag_runs = await get_dagrun_by_dag_id(client, dag_id)
            if dag_runs:
                dag.update({key: dag_runs["dag_runs"][0][key] for key in DAG_RUN_FIELDS})
            dags.append(dag)
    return dags


async def start_by_id(ids):
    transport, auth = await get_httpx_client_settings()
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0), transport=transport, auth=auth) as client:
        for dag_id in ids:
            url = f"{settings.AIRFLOW['URL']}/dags/{dag_id}/dagRuns"
            body = {"note": "app manual trigger"}
            response = await client.post(url, json=body)
            check_response(response)
