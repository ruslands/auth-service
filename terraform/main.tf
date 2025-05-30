terraform {
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "= 0.96.1"
    }
    postgresql = {
      source = "cyrilgdn/postgresql"
    }
  }
  backend "http" {
    address        = "https://git.seller-1.ru/api/v4/projects/31/terraform/state/default"
    lock_address   = "https://git.seller-1.ru/api/v4/projects/31/terraform/state/default/lock"
    lock_method    = "POST"
    unlock_address = "https://git.seller-1.ru/api/v4/projects/31/terraform/state/default/lock"
    unlock_method  = "DELETE"
    retry_wait_min = 5
  }
  required_version = ">= 1.3"
}

provider "yandex" {
  zone                     = "ru-central1-a"
  service_account_key_file = var.yc_service_account_key_file
  cloud_id                 = var.yc_cloud_id
  folder_id                = var.yc_folder_id
  storage_access_key       = var.yc_storage_access_key
  storage_secret_key       = var.yc_storage_secret_key
}
