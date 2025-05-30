


data "yandex_lockbox_secret_version" "development_backend_secret_version" {
  secret_id = local.development_backend_secret_id
}

resource "yandex_iam_service_account" "development_backend" {
  name = "sa-function-development-rtk-auth"
}


# resource "yandex_function" "development_authoriser" {
#   name               = "development-authoriser"
#   user_hash          = var.rtk_functions["development-backend"].sha256_sum
#   runtime            = "python311"
#   entrypoint         = "app.main.wrapper"
#   memory             = "384"
#   execution_timeout  = "10"
#   service_account_id = yandex_iam_service_account.development_backend.id
#   environment = {
#     SECRETS_PROVIDER = "yandex-function"
#   }
#   #  tags               = ["my_tag"]
#   package {
#     bucket_name = module.s3_bucket_functions.bucket_name
#     object_name = var.rtk_functions["development-backend"].object_name
#     sha_256     = var.rtk_functions["development-backend"].sha256_sum
#   }

#   connectivity {
#     network_id = "enp2erfprk8dom0efbbh"
#   }
# }



# service account should be manually added to lockbox binding
# with `lockbox.payloadViewer` permissions


resource "yandex_function" "development_backend" {
  name               = "development-backend"
  user_hash          = var.rtk_functions["development-backend"].sha256_sum
  runtime            = "python311"
  entrypoint         = "app.main.wrapper"
  memory             = "1024"
  execution_timeout  = "60"
  service_account_id = yandex_iam_service_account.development_backend.id
  environment = {
    SECRETS_PROVIDER = "yandex-function"
  }
  #  tags               = ["my_tag"]
  package {
    bucket_name = module.s3_bucket_functions.bucket_name
    object_name = var.rtk_functions["development-backend"].object_name
    sha_256     = var.rtk_functions["development-backend"].sha256_sum
  }

  connectivity {
    network_id = "enp2erfprk8dom0efbbh"
  }

  dynamic "secrets" {
    for_each = toset([for e in data.yandex_lockbox_secret_version.development_backend_secret_version.entries : e.key])
    content {
      id                   = data.yandex_lockbox_secret_version.development_backend_secret_version.secret_id
      version_id           = data.yandex_lockbox_secret_version.development_backend_secret_version.id
      key                  = secrets.key
      environment_variable = secrets.key
    }
  }
}


## Staging authoriser function

# resource "yandex_function" "staging_authoriser" {
#   name               = "staging-authoriser"
#   user_hash          = var.rtk_functions["staging-backend"].sha256_sum
#   runtime            = "python311"
#   entrypoint         = "app.authoriser.main.lambda_handler"
#   memory             = "384"
#   execution_timeout  = "10"
#   service_account_id = yandex_iam_service_account.staging_backend.id
#   environment = {
#     SECRETS_PROVIDER = "yandex-function"
#   }
#   package {
#     bucket_name = module.s3_bucket_functions.bucket_name
#     object_name = var.rtk_functions["staging-backend"].object_name
#     sha_256     = var.rtk_functions["staging-backend"].sha256_sum
#   }

#   dynamic "secrets" {
#     for_each = toset([for e in data.yandex_lockbox_secret_version.staging_backend_secret_version.entries : e.key])
#     content {
#       id                   = data.yandex_lockbox_secret_version.staging_backend_secret_version.secret_id
#       version_id           = data.yandex_lockbox_secret_version.staging_backend_secret_version.id
#       key                  = secrets.key
#       environment_variable = secrets.key
#     }
#   }
#   connectivity {
#     network_id = "enp2erfprk8dom0efbbh"
#   }
# }

## Staging Backend function

data "yandex_lockbox_secret_version" "staging_backend_secret_version" {
  secret_id = local.staging_backend_secret_id
}

# service account should be manually added to lockbox binding
# with `lockbox.payloadViewer` permissions
resource "yandex_iam_service_account" "staging_backend" {
  name = "sa-function-staging-rtk-core"
}

resource "yandex_function" "staging_backend" {
  name               = "staging-backend"
  user_hash          = var.rtk_functions["staging-backend"].sha256_sum
  runtime            = "python311"
  entrypoint         = "app.main.wrapper"
  memory             = "2048"
  execution_timeout  = "60"
  service_account_id = yandex_iam_service_account.staging_backend.id
  #   tags               = ["my_tag"]
  package {
    bucket_name = module.s3_bucket_functions.bucket_name
    object_name = var.rtk_functions["staging-backend"].object_name
    sha_256     = var.rtk_functions["staging-backend"].sha256_sum
  }

  environment = {
    SECRETS_PROVIDER = "yandex-function"
  }

  dynamic "secrets" {
    for_each = toset([for e in data.yandex_lockbox_secret_version.staging_backend_secret_version.entries : e.key])
    content {
      id                   = data.yandex_lockbox_secret_version.staging_backend_secret_version.secret_id
      version_id           = data.yandex_lockbox_secret_version.staging_backend_secret_version.id
      key                  = secrets.key
      environment_variable = secrets.key
    }
  }
  connectivity {
    network_id = "enp2erfprk8dom0efbbh"
  }
}



## Production authoriser function


# resource "yandex_function" "production_authoriser" {
#   name               = "production-authoriser"
#   user_hash          = var.rtk_functions["production-backend"].sha256_sum
#   runtime            = "python311"
#   entrypoint         = "app.authoriser.main.lambda_handler"
#   memory             = "256"
#   execution_timeout  = "10"
#   service_account_id = yandex_iam_service_account.production_backend.id
#   environment = {
#     SECRETS_PROVIDER = "yandex-function"
#   }
#   package {
#     bucket_name = module.s3_bucket_functions.bucket_name
#     object_name = var.rtk_functions["production-backend"].object_name
#     sha_256     = var.rtk_functions["production-backend"].sha256_sum
#   }

#   dynamic "secrets" {
#     for_each = toset([for e in data.yandex_lockbox_secret_version.production_backend_secret_version.entries : e.key])
#     content {
#       id                   = data.yandex_lockbox_secret_version.production_backend_secret_version.secret_id
#       version_id           = data.yandex_lockbox_secret_version.production_backend_secret_version.id
#       key                  = secrets.key
#       environment_variable = secrets.key
#     }
#   }
# }


## Production Backend function

data "yandex_lockbox_secret_version" "production_backend_secret_version" {
  secret_id = local.production_backend_secret_id
}

# service account should be manually added to lockbox binding
# with `lockbox.payloadViewer` permissions
resource "yandex_iam_service_account" "production_backend" {
  name = "sa-function-production-rtk-auth"
}

resource "yandex_function" "production_backend" {
  name               = "production-backend"
  user_hash          = var.rtk_functions["production-backend"].sha256_sum
  runtime            = "python311"
  entrypoint         = "app.main.wrapper"
  memory             = "3072"
  execution_timeout  = "60"
  service_account_id = yandex_iam_service_account.production_backend.id
  #   tags               = ["my_tag"]
  package {
    bucket_name = module.s3_bucket_functions.bucket_name
    object_name = var.rtk_functions["production-backend"].object_name
    sha_256     = var.rtk_functions["production-backend"].sha256_sum
  }

  environment = {
    SECRETS_PROVIDER = "yandex-function"
  }

  dynamic "secrets" {
    for_each = toset([for e in data.yandex_lockbox_secret_version.production_backend_secret_version.entries : e.key])
    content {
      id                   = data.yandex_lockbox_secret_version.production_backend_secret_version.secret_id
      version_id           = data.yandex_lockbox_secret_version.production_backend_secret_version.id
      key                  = secrets.key
      environment_variable = secrets.key
    }
  }
  connectivity {
    network_id = "enp2erfprk8dom0efbbh"
  }
}
