# Authentication and Authorisation service

## Service scope:

* [Authentification](docs/Authentication.md);
* [Authorisation](docs/Authorisation.md);
* [Session management](docs/Session.md);
* [User data management](docs/User.md);
* [Role-Based Access Control](docs/RBAC.md);
* [Team management](docs/Team.md);
* [Visibility Group](docs/Visibility-Group.md);

## Service configuration

* [configuration](docs/Config.md).

## Data models

* [User](docs/models/UserModel.md);
* [Session](docs/models/SessionModel.md);
* [Resource](docs/models/ResourceModel.md);
* [Role](docs/models/RoleModel.md);
* [Permission](docs/models/PermissionModel.md);
* [Team](docs/models/TeamModel.md);
* [Visibility Group](docs/models/VisibilityGroupModel.md);

## Diagrams

**UML** 
* https://plantuml.com/sequence-diagram

**ERD**
* Database tables. 
![erd](./docs/image/erd.png)

## Endpoints for Documentation & Admin panel

* /auth/openapi.json - Openapi
* /auth/admin - Admin panel
* /auth/docs - Swagger documentation
* /auth/redoc - ReDoc documentation
* /auth/mkdocs - MkDocs documentation

## Key Features
- tests on `pytest` with automatic rollback after each test case
- database session stored in python's `context variable`
- configs for `mypy`, `pylint`, `isort` and `black`
- `alembic` for database migrations
- CI/CD with GitLab


## Encryption
* https://cryptography.io/en/latest/hazmat/primitives/asymmetric/serialization/#cryptography.hazmat.primitives.serialization.NoEncryption
* https://github.com/jpadilla/pyjwt/blob/master/jwt/algorithms.py


## Project Directory Structure
```
├── .githooks
    ├── pre-push
├── .github
      ├── workflows
├── api
    ├── endpoints
        ├── v1
        ├── v2
├── app
    ├── module-name
        ├── crud.py
        ├── model.py
        ├── schema.py
    ├── crud.py
    ├── main.py
    ├── model.py
├── core
├── data # SQL scripts for database population
├── deploy
├── docker
├── docs
├── migrations
├── pipelines
    ├── accounts
    ├── admin
├── tests
    ├── api
        ├── test_module-name
    ├── integration
```

Базая структура выглядит следующим образом:
- `core` — ядро, системные вызовы, коннекторы, настройки, не предметно-ориентированный код, а уровень инфраструктуры
- `domain` — предметная область приложения, ключевая часть приложения, где сосредоточеная вся бизнес-логика и взаимодействие с данными  
- `api` — presentation слой, собственно сам api/swagger интерфейс

`domain` в свою очередь, состоит из следующих структур:
- `models` — доменные сущности: таблицы в БД
- `repositories` — коллекции данных, некий стандартизированный интерфейс работы с сущностями, тут не сосредоточена логика, тут есть только относительно тривиальные операции ввода/вывода  
- `schemas` — pydantic-схемы, интерфейсы между всеми компонентами
- `interactors` — это сердце приложения, бизнес-логика, где происходит работа с сущностями/репозиториями, 
валидации/запись/сохранение и так далее, они инжектят в себя репозитории и взаимодействют с ними. Они реализуют use case. Сюда же относится и взаимодействие с внешними сервисами.   

В свою очередь `interactors` реализованы по паттерну CQRS, и предполагают, что разные сервисы будут отвечать за чтение и запись данных (отделение command от query).

Вкратце, получается такая схема:
- `api` взаимодействует с `interactors`
- `interactors` реализуют логику и взаимодействуют с `repositories` по контрактам из `schemas`
- `repositories` взаимодействует с хранилищами (postgres/redis) по контрактам из `schemas`, используя `models` и возвращают данные

## Create JWK

```
from jwcrypto import jwk

key = jwk.JWK.generate(kty='RSA', size=2048, alg='RSA-OAEP-256', use='enc', kid='437y238y4r738h4fj34')
public_key = key.export_public()
private_key = key.export_private()
```

## Использование

```
pip install --user cookiecutter
cookiecutter git@gitlab.masterdelivery.ru:backend/base-template.git
```

## Components 

  - **Python** 
    - [`requirements.txt`](requirements.txt) 
    - linting and testing:
      - ```pre-commit```
      - ```pytest test```

  - **Docker** is used to run locally and in the cloud.
    - [`Dockerfile`](Dockerfile) Dockerfile with multi-architecture support 
    - [`docker-compose`](docker-compose.yml) API Gateway and Lambda functions built from docker image


  - **API** sample routes are mapped to:
    - ```GET /```
    - ```GET /resources``` 
    - ```POST /resources``` 
    - ```PUT /resources/{:id}```
    - ```DELETE /resources/{:id}```
  - 
    - ```GET /tasks``` 
    - ```POST /tasks``` 
    - ```PUT /tasks/{:id}```
    - ```DELETE /tasks/{:id}```

  - **Admin** routes are mapped to:
    - ```GET /admin/```
    - ```GET /admin/{:resource}```
    - ```GET /admin/{:resource}/{:id}```

  
  - **Serverless** API Gateway and functions mapped to lambda-web on cloud (HttpServer locally).
    - [`serverless.yml`](serverless.yml)

  - **Deployment** Actions to deploy on branch commits
    - [.github/workflows](.github/workflows/development.yml) Github actions 
      -  lint   [```feature```]
      -  test   [```feature```]
      -  deploy [```main```, ```production```]
      -  tag    [```production```]



## Creating a new service

Create a new service by selecting the button above :point_down:

<img src="static/assets/images/use-template.png" width="150"> 

> To setup your local environment:

    python -m venv venv
    . ./venv/bin/activate
    pip install -r requirements.txt

### Prepare virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
poetry install
```

## Development

> While working on a feature to start the service locally run: 

      python apps/main.py 

> Or use docker 

      docker-compose up 
      docker-compose up --build

> Before you are ready to merge your feature, to test running lamnbda, you can run: 

      serverless offline 

### Adding a new route

> For CRUD applications, follow the example in [resource.rs](apps/api.routes/resource.rs) and add your resource route to: 
      
      apps/api/routes 

> For example if you are building an API to manage Users and Shares, you would create:
      
      apps/api/routes/users.rs
      apps/api/routes/shares.rs

### Adding a new model

> For admin enabled views, inherit from ```BaseAdmin```. Follow the example [resource.rs](apps/api/models/resource.rs) add your models:

      apps/api/models/users.rs
      apps/api/models/shares.rs

### Backend Tests

```
docker-compose run backend pytest
```

## Migrations

Migrations are run using alembic. To run all migrations and load init data:

```
docker-compose run backend alembic upgrade head
docker-compose run backend python app/initial_data.py
```

To create a new migration:

```
alembic revision -m "create users table"
```

And fill in `upgrade` and `downgrade` methods. For more information see
[Alembic's official documentation](https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script).

### Connecting to a source DB

TODO: Add DB support


### Adding views

Follow the example [resource/dashboard.html](templates/resource/dashboard.html) for a custom model view:

<br/>

## Deploying
 
ToDo

## Features

- **FastAPI** with Python 3.9, totally asynchronous 
- **React 17**
- create-react-app with Typescript
- Postgres
- Redis (PubSub and TimeSeries)
- Celery + Beat
- SQLAlchemy with Alembic for migrations and asynchronous I/O (asyncio) support 
- Pytest for backend tests
- Docker compose for easier development
- Nginx as a reverse proxy to allow backend and frontend on the same port

## Async SQLAlchemy

Parallel database queries with synchronous access
```
➜  ~ wrk -c30 -t3 -d10s  -H "Authorization: bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhcnRlbS5rdXN0aWtvdkBnbWFpbC5jb20iLCJ1aWQiOjUsImZuIjpudWxsLCJsbiI6bnVsbCwicGVybWlzc2lvbnMiOiJ1c2VyIiwiZXhwIjoxNjU0MDIxODg2fQ.439CjqvKtBMvIXBEmH0FLW98Te51ur-VBlTsaS7AkhI" http://localhost:8888/api/users/me  --timeout 5
Running 10s test @ http://localhost:8888/api/users/me
  3 threads and 30 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    49.86ms   23.51ms 167.93ms   67.88%
    Req/Sec   201.13     28.65   343.00     71.00%
  6013 requests in 10.01s, 1.18MB read
Requests/sec:    600.77
Transfer/sec:    121.03KB
```

Parallel database queries with asynchronous access

```
 wrk -c500 -t25 -d10s   -H "Authorization: bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbkBmYXN0YXBpLXJlYWN0LXByb2plY3QuY29tIiwidWlkIjoxLCJmbiI6IkFkbWluIiwibG4iOm51bGwsInBlcm1pc3Npb25zIjoiYWRtaW4iLCJleHAiOjE2NTQwMzQxOTd9.ivCnw0uwce81JdxV7ZHMtl38jVaHUIoD2G95791P634"  http://localhost:8888/api/users/me
Running 10s test @ http://localhost:8888/api/users/me
  25 threads and 500 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   585.91ms  509.32ms   1.99s    79.50%
    Req/Sec    30.16     17.33   160.00     61.57%
  7098 requests in 10.07s, 1.59MB read
  Socket errors: connect 0, read 0, write 0, timeout 316
Requests/sec:    704.59
Transfer/sec:    161.25KB
```

## Continuous Integration

Github workflows are will trigger of off specific branches

- [feature.yml](.github/workflows/feature.yml): Lint and test worflows will run any time there is a push to any feature branch.
- [development.yml](.github/workflows/development.yml): Lint, test and deployment worflows will run any time there is a push to **main** branch.
- [production.yml](.github/workflows/production.yml): Lint, test, deployment and release worflows will run any time there is a push to **main** branch.


This project uses Github workflows.

You will need to configure a role in AWS for the github service to use. Follow the instructions [here](https://github.com/marketplace/actions/aws-assume-role-github-actions).

## Contributing to this template

If you have additions, changes, fixes, create a Pull Request and tag any reviewers and it will be reviewed promptly.

If you are having issues, create an issue and we will investigate.

## How to use it

Go to the directory where you want to create your project and run:

```bash
pip install cookiecutter
cookiecutter https://github.com/tiangolo/full-stack-fastapi-postgresql
```

### Input variables

The generator (cookiecutter) will ask you for some data, you might want to have at hand before generating the project.

The input variables, with their default values (some auto generated) are:

* `project_name`: The name of the project
* `project_slug`: The development friendly name of the project. By default, based on the project name
* `domain_main`: The domain in where to deploy the project for production (from the branch `production`), used by the load balancer, backend, etc. By default, based on the project slug.
* `domain_staging`: The domain in where to deploy while staging (before production) (from the branch `master`). By default, based on the main domain.


## Local environment

To run application in local [AWS Lambda](https://aws.amazon.com/lambda/) environment:

- Run `sam build`
- Run `sam local start-api`

⚠️ For ARM-cpu users: uncomment `Architectures: - arm64` lines in [template.yaml](template.yaml) to build image for the corresponding CPU


## Bitbucket pipeline
image: public.ecr.aws/sam/build-provided # will pick the image from Dockerfile
image: public.ecr.aws/lambda/python:3.9
public.ecr.aws/sam/build-python3.8:1.70.0-20230113014623

## ToDo
[] Move crud from security
[] add isort and other pre-commits <br/>
[] changelog <br/>
[] mkdocs <br/>
[] theneo.io - docs generator <br/>
[] add all possible responses in endpoints for openapi schema <br/>
[] logger debug enable/disable <br/>
[] [test-results, failsafe-reports, test-reports, TestResults, surefire-reports] <br/>
[] Use uvloop <br/>
[] Protect documentation & SQLAdmin endpoints <br/>
[] refresh token rotation <br/>
[] refresh token reuse detection <br/>
[] Observability: x-ray setup <br/>
[] Observability: logger lambda <br/>
[] Observability: ELK setup, APM <br/>
[] Observability: Prometheus, Grafana <br/>
[] Observability: tracing OpenTelemetry, Jaeger <br/>
[] Observability: FastAPI + Elastic APM integration https://www.elastic.co/guide/en/apm/agent/python/master/starlette-support.html <br/>
[] use authlib.jose - for google sign in add jwt signing <br/>
[] make additional user table for supplement data <br/>
[] bitbucket pipeline share the same Docker container between multiple steps <br/>


## License

MIT License

Copyright (c) [2023] [Auth Service]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
