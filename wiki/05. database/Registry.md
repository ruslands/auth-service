## Loading Docker Images on Yandex

1. Request access to the repository [here](https://console.yandex.cloud/folders/b1g4jq10btsa13f1nghg/container-registry/registries).
   
2. Install Yandex CLI using [this guide](https://yandex.cloud/ru/docs/cli/quickstart). Create a profile via federated account:
   ```bash
   yc init --federation-id=bpfg3pbrb12jgdeh0u77
   ```
   
3. Configure Yandex as Docker password storage:
   ```bash
   yc container registry configure-docker
   ```

### Image Preparation

- Dump the database using `pg_dump`. You may need to manually add roles like:
  ```sql
  create role postgres;
  ```

- Create files in a folder:
  - Rename the dump from step 1 to `init.sql`
  - Create a `Dockerfile`:

    ```dockerfile
    FROM timescale/timescaledb:2.9.2-pg14 as dumper

    COPY init.sql /docker-entrypoint-initdb.d/

    RUN ["sed", "-i", "s/exec \"$@\"/echo \"skipping...\"/", "/usr/local/bin/docker-entrypoint.sh"]

    ENV POSTGRES_DB=test_db
    ENV POSTGRES_USER=test_user
    ENV POSTGRES_PASSWORD=test_password
    ENV PGDATA=/data

    RUN ["/usr/local/bin/docker-entrypoint.sh", "postgres"]

    # Final build stage
    FROM timescale/timescaledb:2.9.2-pg14

    COPY --from=dumper /data $PGDATA
    ```

- Build and tag the Docker image:
  ```bash
  docker build . -t cr.yandex/{registry_id}/{image_name}:{tag}
  ```
  Replace `{registry_id}` with `crpipq7k37rtsmu4jig1`, `{image_name}` with `postgres-testdb`, and `{tag}` with a version number.

- Push the image to Yandex:
  ```bash
  docker push cr.yandex/{registry_id}/{image_name}:{tag}
  ```

### Local Deployment with Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.7'

services:
  postgres:
    image: timescale/timescaledb:2.9.2-pg14
    container_name: test1
    ports:
      - "5432:5432"
    volumes:
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
```

Create `.env`:

```
COMPOSE_PROJECT_NAME=test
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
PSQL_PORT=5432
```

For the original guide on database dump in a Docker image, refer to [this link](https://cadu.dev/creating-a-docker-image-with-database-preloaded/).

