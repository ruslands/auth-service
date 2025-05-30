# Create SA
resource "yandex_iam_service_account" "this" {
  folder_id = var.folder_id
  name      = "sa-s3-${var.bucket_name}"
}

# Create Static Access Keys
resource "yandex_iam_service_account_static_access_key" "this" {
  service_account_id = yandex_iam_service_account.this.id
  description        = "Static access key for object storage"
}

resource "yandex_storage_bucket" "this" {
  bucket = var.bucket_name
  dynamic "website" {
    for_each = var.website.enabled ? [1] : []
    content {
      index_document = var.website.index_document
      routing_rules  = var.website.routing_rules
      error_document = var.website.error_document
    }
  }



  # dynamic "grant" {
  #   for_each = var.website.enabled ? [1] : []
  #   content {
  #     type        = "Group"
  #     permissions = ["READ"]
  #     uri         = "http://acs.amazonaws.com/groups/global/AllUsers"
  #   }
  # }
  grant {
    id          = yandex_iam_service_account.this.id
    type        = "CanonicalUser"
    permissions = ["READ", "WRITE"]
  }
  versioning {
    enabled = false
  }
}
