# Authentication and Authorisation service

Service scope:

* [Registration](docs/Registration.md);
* [Authentification](docs/Authentication.md);
* [Authorization](docs/Authorization.md);
* [User blocking](docs/Blocking.md);
* [User session management](docs/Session.md);
* [User data management](docs/User.md).

The service uses PostgresSQL to store user and session data.
Also session data is cached in Redis.


## Service configuration

* [configuration](docs/Config.md).


## Data models

* [Client](docs/models/ClientModel.md);
* [User](docs/models/UserModel.md);
* [Session](docs/models/SessionModel.md).


## UML diagrams

* https://plantuml.com/sequence-diagram


## Endpoints for Documentation & Admin panel

* /auth/openapi.json - Openapi
* /auth/admin - Admin panel
* /auth/docs - Swagger documentation
* /auth/redoc - ReDoc documentation
* /auth/mkdocs - MkDocs documentation


## Encryption
* https://cryptography.io/en/latest/hazmat/primitives/asymmetric/serialization/#cryptography.hazmat.primitives.serialization.NoEncryption
* https://github.com/jpadilla/pyjwt/blob/master/jwt/algorithms.py


## Local environment

To run application in local [AWS Lambda](https://aws.amazon.com/lambda/) environment:

- Run `sam build`
- Run `sam local start-api`

⚠️ For ARM-cpu users: uncomment `Architectures: - arm64` lines in [template.yaml](template.yaml) to build image for the corresponding CPU

## Bitbucket pipeline
image: public.ecr.aws/sam/build-provided # will pick the image from Dockerfile
image: public.ecr.aws/lambda/python:3.9
public.ecr.aws/sam/build-python3.8:1.70.0-20230113014623

## ToDo list
- [ ] changelog
- [ ] mkdocs
- [ ] www.theneo.io
- [ ] add all responses for openapi schema 
- [ ] logger debug enable/disable
- [ ] [test-results, failsafe-reports, test-reports, TestResults, surefire-reports]
- [ ] Protect SQLAdmin endpoint
- [ ] Use uvloop
- [ ] mangum read
- [ ] Protect docs
- [ ] split databases development-EC2 & development-serverless
- [ ] use authlib.jose - for google sign in add jwt signing
- [ ] make extra user table for supplement data
- [ ] refresh token rotation
- [ ] refresh token reuse detection
- [ ] Observability: x-ray setup
- [ ] Observability: logger lambda
- [ ] Observability: ELK setup, APM
- [ ] Observability: Prometheus, Grafana
- [ ] Observability: tracing OpenTelemetry, Jaeger
- [ ] Observability: FastAPI + Elastic APM integration
        https://www.elastic.co/guide/en/apm/agent/python/master/starlette-support.html
- [ ] use authlib.jose - for google sign in add jwt signing
- [ ] make extra user table for supplement data
- [ ] bitbucket pipeline share the same Docker container between multiple steps