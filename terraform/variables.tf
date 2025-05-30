variable "yc_cloud_id" {
  type        = string
  default     = "b1gpce3t7v8er4vl760m"
  description = "Yandex Cloud Id"
}

variable "yc_folder_id" {
  type        = string
  default     = "b1g4jq10btsa13f1nghg"
  description = "Yandex Cloud Folder Id"
}

variable "yc_service_account_key_file" {
  type        = string
  sensitive   = true
  description = "Yandex Service Account Key file"
}

variable "yc_storage_access_key" {
  type        = string
  sensitive   = true
  description = "Yandex Storage Access key"
}

variable "yc_storage_secret_key" {
  type        = string
  sensitive   = true
  description = "Yandex Storage Secret key"
}

variable "database_production_proedcstpq_password" {
  default = ""

}

variable "database_production_prodwriterobot_password" {
  default = ""

}

variable "database_staging_stagwriterobot_password" {
  default = ""

}

variable "database_development_devwriterobot_password" {
  default = ""

}

variable "database_staging_stabdteuwi_password" {
  default = ""

}

variable "database_development_devetgyuso_password" {
  default = ""

}

variable "user_read_development_production_password" {
  default = ""

}

variable "user_read_development_staging_password" {
  default = ""

}

variable "user_read_development_development_password" {
  default = ""

}

variable "user_dev1_password" {
  default = ""

}

variable "user_dev_read_write_password" {
  default = ""

}

variable "user_sta_read_write_password" {
  default = ""

}

variable "user_pro_read_write_password" {
  default = ""

}
variable "user1_dev_read_write_password" {
  default = ""

}

variable "redis_password" {
  default = ""

}

variable "rtk_functions" {
  type = map(object({
    sha256_sum  = string
    object_name = string
  }))
}


variable "image_tag" {
  type        = string
  description = "The tag for the Docker image"
  default     = "latest"
}
