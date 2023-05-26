FROM public.ecr.aws/sam/build-python3.9:1.70.0-20230113014543

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app"

RUN pip install -U pip setuptools wheel
RUN pip install poetry
RUN pip install awslambdaric

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false

RUN poetry install --no-root


COPY ./ ./
RUN chmod +x entrypoint.sh

ENTRYPOINT ["python", "-m", "awslambdaric"]
CMD ["app.main.wrapper"]