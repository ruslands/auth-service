Вот отформатированная и дополненная версия в Markdown:

# Terraform

[[_TOC_]]

## Настройка проекта

1. **Создание токена**  
   Создаем [Gitlab Personal Access Token](https://git.ru/-/profile/personal_access_tokens) с необходимыми правами (рекомендуется scope: `write_repository`).

2. **Установка утилит**  
   Устанавливаем необходимые инструменты для работы с Terraform:
   
   ```sh
   brew install terraform
   ```

3. **Инициализация проекта**  
   Настраиваем переменные окружения и инициализируем Terraform с бэкендом Gitlab:
   
   ```sh
   GITLAB_USERNAME=my-gitlab-username
   GITLAB_PASSWORD=my-secret-private-token

   terraform init \
       -backend-config="username=$GITLAB_USERNAME" \
       -backend-config="password=$GITLAB_PASSWORD"
   ```

4. **Создание файла секретов**  
   Создаем файл `secrets.auto.tfvars` в корне проекта и заполняем необходимые переменные, например:
   
   ```
   variable_name = "value"
   ```


## Внесение изменений

1. **Создание ветки**  
   Создаем новую ветку для внесения изменений:
   
   ```sh
   git checkout -b feature/my-changes
   ```

2. **Форматирование и валидация**  
   Форматируем код и проверяем его корректность:
   
   ```sh
   terraform fmt -check -diff
   terraform validate
   ```

3. **Проверка плана локально**  
   Проверяем план изменений без блокировки состояния:
   
   ```sh
   terraform plan -lock=false
   ```

4. **Коммит и пуш**  
   Фиксируем изменения и отправляем их в репозиторий:
   
   ```sh
   git add .
   git commit -m "Add my changes"
   git push origin feature/my-changes
   ```

5. **Создание Merge Request**  
   Открываем Merge Request в Gitlab и ожидаем завершения запущенного пайплайна.

6. **Проверка плана в CI/CD**  
   Проверяем вывод `terraform-plan` в логах джобы. Если всё корректно, мержим изменения в `default`-ветку.

7. **Проверка в default-ветке**  
   После мержа ждем завершения пайплайна в `default`-ветке, еще раз убеждаемся, что `terraform-plan` содержит ожидаемые изменения.

8. **Применение изменений**  
   Вручную запускаем шаг `terraform:apply` для применения изменений:
   
   ```sh
   terraform apply
   ```

## При обновлении версии секретов

1. **Перезапуск Pipeline**  
   Запускаем пайплайн вручную для обновления секретов в Terraform state:
   
   - Перейти в Gitlab → CI/CD → Pipelines → Run Pipeline.

## Права на проект

1. **Необходимые права**  
   Для пользователей, выполняющих деплой, требуются права уровня **Maintainer** в проекте.


# RTK-Terraform

[[_TOC_]]

## Настройка проекта

1. **Создание токена**  
   Создаем [Gitlab Personal Access Token](https://git.ru/-/profile/personal_access_tokens) с необходимыми правами (рекомендуется scope: `api`).

2. **Установка утилит**  
   Устанавливаем необходимые инструменты для работы с Terraform:
   
   ```sh
   brew install terraform
   ```

3. **Инициализация проекта**  
   Настраиваем переменные окружения и инициализируем Terraform с бэкендом Gitlab:
   
   ```sh
   GITLAB_USERNAME=my-gitlab-username
   GITLAB_PASSWORD=my-secret-private-token

   terraform init \
       -backend-config="username=$GITLAB_USERNAME" \
       -backend-config="password=$GITLAB_PASSWORD"
   ```

4. **Создание файла секретов**  
   Создаем файл `secrets.auto.tfvars` в корне проекта и заполняем необходимые переменные, например:
   
   ```
   variable_name = "value"
   ```

5. **Готовность к работе**  
   Проект готов к использованию.

## Внесение изменений

1. **Создание ветки**  
   Создаем новую ветку для внесения изменений:
   
   ```sh
   git checkout -b feature/my-changes
   ```

2. **Форматирование и валидация**  
   Форматируем код и проверяем его корректность:
   
   ```sh
   terraform fmt -check -diff
   terraform validate
   ```

3. **Проверка плана локально**  
   Проверяем план изменений без блокировки состояния:
   
   ```sh
   terraform plan -lock=false
   ```

4. **Коммит и пуш**  
   Фиксируем изменения и отправляем их в репозиторий:
   
   ```sh
   git add .
   git commit -m "Add my changes"
   git push origin feature/my-changes
   ```

5. **Создание Merge Request**  
   Открываем Merge Request в Gitlab и ожидаем завершения запущенного пайплайна.

6. **Проверка плана в CI/CD**  
   Проверяем вывод `terraform-plan` в логах джобы. Если всё корректно, мержим изменения в `default`-ветку.

7. **Проверка в default-ветке**  
   После мержа ждем завершения пайплайна в `default`-ветке, еще раз убеждаемся, что `terraform-plan` содержит ожидаемые изменения.

8. **Применение изменений**  
   Вручную запускаем шаг `terraform:apply` для применения изменений:
   
   ```sh
   terraform apply
   ```

## При обновлении версии секретов

1. **Перезапуск Pipeline**  
   Запускаем пайплайн вручную для обновления секретов в Terraform state:
   
   - Перейти в Gitlab → CI/CD → Pipelines → Run Pipeline.

## Права на проект

1. **Необходимые права**  
   Для пользователей, выполняющих деплой, требуются права уровня **Maintainer** в проекте.
