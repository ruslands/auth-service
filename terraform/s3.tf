module "s3_bucket_functions" {
  source      = "./modules/s3_bucket"
  bucket_name = "rtk-functions"
  folder_id   = var.yc_folder_id
}

module "s3_bucket_static_staging" {
  source      = "./modules/s3_bucket"
  bucket_name = "staging-seller-1"
  folder_id   = var.yc_folder_id
  website = {
    enabled        = true
    error_document = "index.html"
  }
}

module "s3_bucket_static_production" {
  source      = "./modules/s3_bucket"
  bucket_name = "production-seller-1"
  folder_id   = var.yc_folder_id
  website = {
    enabled        = true
    error_document = "index.html"
  }
}

module "s3_bucket_static_development" {
  source      = "./modules/s3_bucket"
  bucket_name = "development-seller-1"
  folder_id   = var.yc_folder_id
  website = {
    enabled        = true
    error_document = "index.html"
  }
}

module "s3_bucket_static_landing" {
  source      = "./modules/s3_bucket"
  bucket_name = "landing-seller-1"
  folder_id   = var.yc_folder_id
  website = {
    enabled        = true
    error_document = "index.html"
  }
}

