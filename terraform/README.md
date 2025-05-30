# rtk-terraform

[[_TOC_]]

## Настройка проекта

1. Создаем [Gitlab Personal token](https://git.seller-1.ru/-/profile/personal_access_tokens)

1. Устанавливаем необходимые утилиты:

    ```sh
    brew install terraform
    ```

1. Инициализируем проект:

    ```sh
    GITLAB_USERNAME=my-gitlab-username
    GITLAB_PASSWORD=my-secret-private-token

    terraform init \
        -backend-config="username=$GITLAB_USERNAME" \
        -backend-config="password=$GITLAB_PASSWORD"
    ```

1. Создаем файл `secrets.auto.tfvars` в корне проекта и заполняем необходимые переменные.

1. Можно работать с проектом

## Внесение изменений

1. Создаем новую ветку и вносим изменения

1. Форматируем и проверяем код:

    ```sh
    terraform fmt -check -diff
    terraform validate
    ```

1. Проверяем terraform plan локально:

    ```sh
    terraform plan -lock=false
    ```

1. Делаем коммит и пуш в репозиторий

1. Открываем Gitlab MR и ждем запущенный пайплайн

1. Проверяем terraform-plan (в логах джобы) и, если всё ок, мержим измения в default-ветку

1. Ждем пайплайн в default-ветке, еще раз убеждаемся, что terraform-plan содержит
    ожидаемые изменения

1. Вручную запускаем последний шаг `terraform:apply` для применения изменений

## При обновлении версии secrets

1. Запустить Pipeline 

## Права на проект 

1. для users которые деплоят необходимы права Maintainer

