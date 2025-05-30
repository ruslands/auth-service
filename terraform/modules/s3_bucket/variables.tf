variable "bucket_name" {
  type        = string
  description = "S3 bucket name"
}

variable "folder_id" {
  type        = string
  description = "Yandex Cloud folder Id"
}

variable "website" {
  type = object({
    enabled        = optional(bool, false)
    index_document = optional(string, "index.html")
    error_document = optional(string, null)
    routing_rules  = optional(string, null)
  })
  default     = {}
  description = "Website configuration"
}
