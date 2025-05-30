// Создание бакета с использованием ключа
resource "yandex_storage_bucket" "media-development-seller-1" {
  bucket    = "media-development-seller-1"
  folder_id = var.yc_folder_id
  grant {
    id          = module.s3_bucket_static_development.service_account_id
    type        = "CanonicalUser"
    permissions = ["READ", "WRITE"]
  }
  anonymous_access_flags {
    read        = true
    list        = true
    config_read = false
  }
}
resource "yandex_storage_bucket" "media-staging-seller-1" {
  bucket    = "media-staging-seller-1"
  folder_id = var.yc_folder_id
  grant {
    id          = module.s3_bucket_static_staging.service_account_id
    type        = "CanonicalUser"
    permissions = ["READ", "WRITE"]
  }
  anonymous_access_flags {
    read        = true
    list        = true
    config_read = false
  }
}
resource "yandex_storage_bucket" "media-production-seller-1" {
  bucket    = "media-production-seller-1"
  folder_id = var.yc_folder_id
  grant {
    id          = module.s3_bucket_static_production.service_account_id
    type        = "CanonicalUser"
    permissions = ["READ", "WRITE"]
  }
  anonymous_access_flags {
    read        = true
    list        = true
    config_read = false
  }
}
