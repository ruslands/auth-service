locals {
  # Список Id функций, которыые будут вызваны в API Gateway
  # (используется ниже для назначение разрешений на запуск)
  staging_function_ids = [
    yandex_function.staging_backend.id,
  ]
}

data "yandex_cm_certificate" "seller_1_ru" {
  name = "seller-1-ru"
}

resource "yandex_iam_service_account" "staging_api_gateway" {
  name = "sa-api-gateway-staging"
}

resource "yandex_function_iam_binding" "staging_api_gateway_sa_binding" {
  count       = length(local.staging_function_ids)
  function_id = local.staging_function_ids[count.index]
  role        = "serverless.functions.invoker"

  members = [
    "serviceAccount:${yandex_iam_service_account.staging_api_gateway.id}",
  ]
}

resource "yandex_api_gateway" "staging_api_gateway" {
  depends_on = [
    yandex_function.staging_backend,
    #yandex_function.staging_core,
  ]
  name        = "staging-api-gateway"
  description = "Staging API Gateway"
  custom_domains {
    fqdn           = "staging.seller-1.ru"
    certificate_id = data.yandex_cm_certificate.seller_1_ru.id
  }
  spec = <<-EOT
openapi: "3.0.0"
info:
  version: 1.0.0
  title: Test API
paths:
  /:
    get:
      summary: Serve static file from Yandex Cloud Object Storage
      x-yc-apigateway-integration:
        type: object_storage
        bucket: ${module.s3_bucket_static_staging.bucket_name}
        object: 'index.html'
        service_account_id: ${module.s3_bucket_static_staging.service_account_id}
  /{file+}:
    get:
      summary: Serve static file from Yandex Cloud Object Storage
      parameters:
        - name: file
          in: path
          required: false
          schema:
            type: string
      x-yc-apigateway-integration:
        type: object_storage
        bucket: ${module.s3_bucket_static_staging.bucket_name}
        object: '{file}'
        error_object: 'index.html'
        service_account_id: ${module.s3_bucket_static_staging.service_account_id}
  /media/{file+}:
    get:
      summary: Serve static file from Yandex Cloud Object Storage
      parameters:
        - name: file
          in: path
          required: false
          schema:
            type: string
      x-yc-apigateway-integration:
        type: object_storage
        bucket: ${yandex_storage_bucket.media-staging-seller-1.bucket}
        object: '{file}'
      #  error_object: 'index.html'
        service_account_id: ${module.s3_bucket_static_staging.service_account_id}         
  # /admin/{proxy+}:
  #   x-yc-apigateway-any-method:
  #     x-yc-apigateway-integration:
  #       type: cloud_functions
  #       function_id: ${yandex_function.staging_backend.id}
  #       service_account_id: ${yandex_iam_service_account.staging_api_gateway.id}
  #       payload_format_version: '1.0'
  #     parameters:
  #     - explode: false
  #       in: path
  #       name: proxy
  #       required: false
  #       schema:
  #         default: '-'
  #         type: string
  #       style: simple     
  /docs/{proxy+}:
    x-yc-apigateway-any-method:
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: ${yandex_function.staging_backend.id}
        service_account_id: ${yandex_iam_service_account.staging_api_gateway.id}
        payload_format_version: '1.0'
      parameters:
      - explode: false
        in: path
        name: proxy
        required: false
        schema:
          default: '-'
          type: string
        style: simple    
  /redoc/{proxy+}:
    x-yc-apigateway-any-method:
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: ${yandex_function.staging_backend.id}
        service_account_id: ${yandex_iam_service_account.staging_api_gateway.id}
        payload_format_version: '1.0'
      parameters:
      - explode: false
        in: path
        name: proxy
        required: false
        schema:
          default: '-'
          type: string
        style: simple  
  /openapi.json/{proxy+}:
    x-yc-apigateway-any-method:
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: ${yandex_function.staging_backend.id}
        service_account_id: ${yandex_iam_service_account.staging_api_gateway.id}
        payload_format_version: '1.0'
      parameters:
      - explode: false
        in: path
        name: proxy
        required: false
        schema:
          default: '-'
          type: string
        style: simple                      
  /api/v1/{proxy+}:
    x-yc-apigateway-any-method:
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: ${yandex_function.staging_backend.id}
        service_account_id: ${yandex_iam_service_account.staging_api_gateway.id}
        payload_format_version: '1.0'
      parameters:
      - explode: false
        in: path
        name: proxy
        required: false
        schema:
          default: '-'
          type: string
        style: simple
EOT
}
#      security:
#       - httpBearerAuth: [ ]
# components:
#   securitySchemes:
#     httpBearerAuth:
#       type: http
#       scheme: bearer
#       x-yc-apigateway-authorizer:
#         type: function
#         function_id: ${yandex_function.staging_authoriser.id}
#         service_account_id: ${yandex_iam_service_account.staging_api_gateway.id}
#         authorizer_result_ttl_in_seconds: 300
