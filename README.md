# Authentication and Authorisation service

Service scope:

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


## ToDo
- [ ] add isort and other pre-commits
- [ ] changelog
- [ ] mkdocs
- [ ] theneo.io - docs generator
- [ ] add all possible responses in endpoints for openapi schema 
- [ ] logger debug enable/disable
- [ ] [test-results, failsafe-reports, test-reports, TestResults, surefire-reports]
- [ ] Use uvloop
- [ ] Protect documentation & SQLAdmin endpoints
- [ ] refresh token rotation
- [ ] refresh token reuse detection
- [ ] Observability: x-ray setup
- [ ] Observability: logger lambda
- [ ] Observability: ELK setup, APM
- [ ] Observability: Prometheus, Grafana
- [ ] Observability: tracing OpenTelemetry, Jaeger
- [ ] Observability: FastAPI + Elastic APM integration https://www.elastic.co/guide/en/apm/agent/python/master/starlette-support.html
- [ ] use authlib.jose - for google sign in add jwt signing
- [ ] make additional user table for supplement data
- [ ] bitbucket pipeline share the same Docker container between multiple steps