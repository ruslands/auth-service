FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app"

RUN pip install -U pip setuptools wheel
RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false

RUN poetry install --no-root

COPY ./ ./
RUN chmod +x entrypoint.sh

EXPOSE 8000
ENTRYPOINT [ "./entrypoint.sh" ]
CMD [ "uvicorn", "app.main:app", "--port", "8000", "--host", "0.0.0.0", "--reload", "--forwarded-allow-ips=*", "--proxy-headers" ]

# "gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80"
