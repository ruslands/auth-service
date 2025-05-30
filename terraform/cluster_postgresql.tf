resource "yandex_mdb_postgresql_cluster" "production_cluster_seller" {
  name                = "production_cluster_seller"
  environment         = "PRODUCTION"
  network_id          = "enp2erfprk8dom0efbbh"
  deletion_protection = false

  config {
    version = "14"
    resources {
      resource_preset_id = "c3-c4-m8"
      disk_type_id       = "network-ssd"
      disk_size          = 50
    }
    postgresql_config = {
      auto_explain_log_analyze      = true
      auto_explain_log_buffers      = false
      auto_explain_log_min_duration = 500
      auto_explain_log_triggers     = true
      shared_preload_libraries      = "SHARED_PRELOAD_LIBRARIES_TIMESCALEDB,SHARED_PRELOAD_LIBRARIES_AUTO_EXPLAIN"
    }
    backup_window_start {
      hours   = 01
      minutes = 00
    }
  }

  host {
    zone             = "ru-central1-b"
    name             = "db1"
    subnet_id        = "e2lpg52vf357d83h50p3"
    assign_public_ip = true
  }
}

# database production 

resource "yandex_mdb_postgresql_database" "production" {
  cluster_id = yandex_mdb_postgresql_cluster.production_cluster_seller.id
  name       = "production"
  owner      = "proedcstpq"
  lc_collate = "en_US.UTF-8"
  lc_type    = "en_US.UTF-8"
  depends_on = [
    yandex_mdb_postgresql_user.proedcstpq
  ]
  extension {
    name = "uuid-ossp"
  }
  extension {
    name = "pg_stat_statements"
  }
  extension {
    name = "pg_trgm"
  }
  extension {
    name    = "timescaledb"
    version = "2.4.2"
  }

  lifecycle {
    ignore_changes = [extension]
  }

}

# database production user proedcstpq

resource "yandex_mdb_postgresql_user" "proedcstpq" {
  cluster_id          = yandex_mdb_postgresql_cluster.production_cluster_seller.id
  name                = "proedcstpq"
  deletion_protection = false
  conn_limit          = "200"
  password            = var.database_production_proedcstpq_password
  lifecycle {
    create_before_destroy = true
  }
}


# database staging

resource "yandex_mdb_postgresql_database" "staging" {
  cluster_id = yandex_mdb_postgresql_cluster.production_cluster_seller.id
  name       = "staging"
  owner      = "stabdteuwi"
  lc_collate = "en_US.UTF-8"
  lc_type    = "en_US.UTF-8"
  depends_on = [
    yandex_mdb_postgresql_user.stabdteuwi
  ]
  extension {
    name = "uuid-ossp"
  }
  extension {
    name    = "timescaledb"
    version = "2.4.2"
  }

  lifecycle {
    ignore_changes = [extension]
  }

}

# database staging user stabdteuwi

resource "yandex_mdb_postgresql_user" "stabdteuwi" {
  cluster_id          = yandex_mdb_postgresql_cluster.production_cluster_seller.id
  deletion_protection = false
  name                = "stabdteuwi"
  conn_limit          = "200"
  password            = var.database_staging_stabdteuwi_password
}

# database development

resource "yandex_mdb_postgresql_database" "development" {
  cluster_id = yandex_mdb_postgresql_cluster.production_cluster_seller.id
  name       = "development"
  owner      = "devetgyuso"
  lc_collate = "en_US.UTF-8"
  lc_type    = "en_US.UTF-8"
  depends_on = [
    yandex_mdb_postgresql_user.devetgyuso
  ]
  extension {
    name = "uuid-ossp"
  }
  extension {
    name = "pg_trgm"
  }
  extension {
    name    = "timescaledb"
    version = "2.4.2"
  }

  lifecycle {
    ignore_changes = [extension]
  }

}

# database development user devetgyuso

resource "yandex_mdb_postgresql_user" "devetgyuso" {
  cluster_id          = yandex_mdb_postgresql_cluster.production_cluster_seller.id
  deletion_protection = false
  name                = "devetgyuso"
  conn_limit          = "30"
  password            = var.database_development_devetgyuso_password
}

resource "yandex_vpc_security_group" "pgsql-prod" {
  name       = "pgsql-prod"
  network_id = "enp2erfprk8dom0efbbh"

  ingress {
    description    = "PostgreSQL"
    port           = 6432
    protocol       = "TCP"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}

# database production user prod_write_robot

resource "yandex_mdb_postgresql_user" "prodwriterobot" {
  cluster_id = yandex_mdb_postgresql_cluster.production_cluster_seller.id
  name       = "prodwriterobot"
  conn_limit = "10"
  password   = var.database_production_prodwriterobot_password
  permission {
    database_name = yandex_mdb_postgresql_database.production.name
  }
}

resource "yandex_mdb_postgresql_user" "stagwriterobot" {
  cluster_id = yandex_mdb_postgresql_cluster.production_cluster_seller.id
  name       = "stagwriterobot"
  conn_limit = "10"
  password   = var.database_staging_stagwriterobot_password
  permission {
    database_name = yandex_mdb_postgresql_database.staging.name
  }
}

resource "yandex_mdb_postgresql_user" "devwriterobot" {
  cluster_id = yandex_mdb_postgresql_cluster.production_cluster_seller.id
  name       = "devwriterobot"
  conn_limit = "10"
  password   = var.database_development_devwriterobot_password
  permission {
    database_name = yandex_mdb_postgresql_database.development.name
  }
}

# resource "yandex_mdb_postgresql_user" "user1" {
#   cluster_id = yandex_mdb_postgresql_cluster.production_cluster_seller.id
#   login      = true
#   grants     = ["dev_read_write", "sta_read_write", "pro_read_write"]
#   name       = "user1"
#   conn_limit = "5"
#   password   = var.user1_dev_read_write_password
#   permission {
#     database_name = yandex_mdb_postgresql_database.development.name
#   }
# }

resource "yandex_mdb_postgresql_user" "sta_read_write" {
  cluster_id = yandex_mdb_postgresql_cluster.production_cluster_seller.id
  name       = "sta_read_write"
  conn_limit = "5"
  password   = var.user_sta_read_write_password
  permission {
    database_name = yandex_mdb_postgresql_database.staging.name
  }
}

resource "yandex_mdb_postgresql_user" "dev_read_write" {
  cluster_id = yandex_mdb_postgresql_cluster.production_cluster_seller.id
  name       = "dev_read_write"
  conn_limit = "5"
  password   = var.user_dev_read_write_password
  permission {
    database_name = yandex_mdb_postgresql_database.development.name
  }
}

resource "yandex_mdb_postgresql_user" "pro_read_write" {
  cluster_id = yandex_mdb_postgresql_cluster.production_cluster_seller.id
  name       = "pro_read_write"
  conn_limit = "5"
  password   = var.user_pro_read_write_password
  permission {
    database_name = yandex_mdb_postgresql_database.production.name
  }
}


resource "yandex_mdb_postgresql_user" "read_development_production" {
  cluster_id = yandex_mdb_postgresql_cluster.production_cluster_seller.id
  name       = "read_development_production"
  conn_limit = "10"
  password   = var.user_read_development_production_password
  permission {
    database_name = yandex_mdb_postgresql_database.production.name
  }
}

resource "yandex_mdb_postgresql_user" "read_development_staging" {
  cluster_id = yandex_mdb_postgresql_cluster.production_cluster_seller.id
  name       = "read_development_staging"
  conn_limit = "10"
  password   = var.user_read_development_staging_password
  permission {
    database_name = yandex_mdb_postgresql_database.staging.name
  }
}

resource "yandex_mdb_postgresql_user" "read_development_development" {
  cluster_id = yandex_mdb_postgresql_cluster.production_cluster_seller.id
  name       = "read_development_development"
  conn_limit = "10"
  password   = var.user_read_development_development_password
  permission {
    database_name = yandex_mdb_postgresql_database.development.name
  }
}


provider "postgresql" {
  host     = yandex_mdb_postgresql_cluster.production_cluster_seller.host[0].fqdn
  port     = 6432
  database = yandex_mdb_postgresql_database.production.name
  username = yandex_mdb_postgresql_user.proedcstpq.name
  password = var.database_production_proedcstpq_password
}

provider "postgresql" {
  alias    = "staging"
  host     = yandex_mdb_postgresql_cluster.production_cluster_seller.host[0].fqdn
  port     = 6432
  database = yandex_mdb_postgresql_database.staging.name
  username = yandex_mdb_postgresql_user.stabdteuwi.name
  password = var.database_staging_stabdteuwi_password
}

provider "postgresql" {
  alias    = "development"
  host     = yandex_mdb_postgresql_cluster.production_cluster_seller.host[0].fqdn
  port     = 6432
  database = yandex_mdb_postgresql_database.development.name
  username = yandex_mdb_postgresql_user.devetgyuso.name
  password = var.database_development_devetgyuso_password
}


# Grand select,update,insert,usage production for prodwriterobot

resource "postgresql_grant" "prodwriterobot_schema_core" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.prodwriterobot.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "core"
  lifecycle {
    create_before_destroy = true
  }
}
resource "postgresql_grant" "prodwriterobot_schema_auth" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.prodwriterobot.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "auth"
}
resource "postgresql_grant" "prodwriterobot_schema_source" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.prodwriterobot.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "source"
}
resource "postgresql_grant" "prodwriterobot_tables_core" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.prodwriterobot.name
  object_type = "table"
  privileges  = ["SELECT", "UPDATE", "INSERT"]
  schema      = "core"
}
resource "postgresql_grant" "prodwriterobot_tables_auth" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.prodwriterobot.name
  object_type = "table"
  privileges  = ["SELECT", "UPDATE", "INSERT"]
  schema      = "auth"
}
resource "postgresql_grant" "prodwriterobot_tables_source" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.prodwriterobot.name
  object_type = "table"
  privileges  = ["SELECT", "UPDATE", "INSERT"]
  schema      = "source"
}
# Grand select,usage production for read_development_production

resource "postgresql_grant" "readonly_schema_core" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.read_development_production.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "core"
}
resource "postgresql_grant" "readonly_schema_analytics" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.read_development_production.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "analytics"
}
resource "postgresql_grant" "readonly_schema_auth" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.read_development_production.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "auth"
}
resource "postgresql_grant" "readonly_schema_source" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.read_development_production.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "source"
}
resource "postgresql_grant" "readonly_tables_core" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.read_development_production.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "core"
}
resource "postgresql_grant" "readonly_tables_analytics" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.read_development_production.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "analytics"
}
resource "postgresql_grant" "readonly_tables_auth" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.read_development_production.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "auth"
}
resource "postgresql_grant" "readonly_tables_source" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.read_development_production.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "source"
}

# Grand select,usage staging for read_development

resource "postgresql_grant" "readonly_schema_analytics_staging" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.read_development_staging.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "analytics"
}
resource "postgresql_grant" "readonly_schema_core_staging" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.read_development_staging.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "core"
}
resource "postgresql_grant" "readonly_schema_auth_staging" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.read_development_staging.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "auth"
}
resource "postgresql_grant" "readonly_schema_source_staging" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.read_development_staging.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "source"
}
resource "postgresql_grant" "readonly_tables_core_staging" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.read_development_staging.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "core"
}
resource "postgresql_grant" "readonly_tables_analytics_staging" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.read_development_staging.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "analytics"
}
resource "postgresql_grant" "readonly_tables_auth_staging" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.read_development_staging.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "auth"
}
resource "postgresql_grant" "readonly_tables_source_staging" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.read_development_staging.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "source"
}

# Grand select,update,insert,usage staging for stagwriterobot

resource "postgresql_grant" "stagwriterobot_schema_core_staging" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.stagwriterobot.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "core"
}
resource "postgresql_grant" "stagwriterobot_schema_auth_staging" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.stagwriterobot.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "auth"
}
resource "postgresql_grant" "stagwriterobot_schema_source_staging" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.stagwriterobot.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "source"
}
resource "postgresql_grant" "stagwriterobot_tables_core_staging" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.stagwriterobot.name
  object_type = "table"
  privileges  = ["SELECT", "UPDATE", "INSERT"]
  schema      = "core"
}
resource "postgresql_grant" "stagwriterobot_tables_auth_staging" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.stagwriterobot.name
  object_type = "table"
  privileges  = ["SELECT", "UPDATE", "INSERT"]
  schema      = "auth"
}
resource "postgresql_grant" "stagwriterobot_tables_source_staging" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.stagwriterobot.name
  object_type = "table"
  privileges  = ["SELECT", "UPDATE", "INSERT"]
  schema      = "source"
}

# # Grand select,usage development for read_development
resource "postgresql_grant" "readonly_schema_core_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.read_development_development.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "core"
}
resource "postgresql_grant" "readonly_schema_auth_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.read_development_development.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "auth"
}
resource "postgresql_grant" "readonly_schema_source_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.read_development_development.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "source"
}
resource "postgresql_grant" "readonly_tables_core_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.read_development_development.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "core"
}
resource "postgresql_grant" "readonly_tables_auth_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.read_development_development.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "auth"
}
resource "postgresql_grant" "readonly_tables_source_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.read_development_development.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "source"
}

# Grand select,update,insert,usage staging for devwriterobot

resource "postgresql_grant" "devwriterobot_schema_core_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.devwriterobot.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "core"
}
resource "postgresql_grant" "devwriterobot_schema_auth_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.devwriterobot.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "auth"
}
resource "postgresql_grant" "devwriterobot_schema_source_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.devwriterobot.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "source"
}
resource "postgresql_grant" "devwriterobot_tables_core_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.devwriterobot.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "core"
}
resource "postgresql_grant" "devwriterobot_tables_auth_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.devwriterobot.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "auth"
}
resource "postgresql_grant" "devwriterobot_tables_source_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.devwriterobot.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "source"
}

# Grand select,update,insert,usage development for read_write

resource "postgresql_grant" "dev_read_write_schema_core_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.dev_read_write.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "core"
}
resource "postgresql_grant" "dev_read_write_schema_auth_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.dev_read_write.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "auth"
}
resource "postgresql_grant" "dev_read_write_schema_source_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.dev_read_write.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "source"
}
resource "postgresql_grant" "dev_read_write_tables_core_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.dev_read_write.name
  object_type = "table"
  privileges  = ["SELECT", "UPDATE", "INSERT"]
  schema      = "core"
}
resource "postgresql_grant" "dev_read_write_tables_auth_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.dev_read_write.name
  object_type = "table"
  privileges  = ["SELECT", "UPDATE", "INSERT"]
  schema      = "auth"
}
resource "postgresql_grant" "dev_read_write_tables_source_dev" {
  provider    = postgresql.development
  database    = yandex_mdb_postgresql_database.development.name
  role        = yandex_mdb_postgresql_user.dev_read_write.name
  object_type = "table"
  privileges  = ["SELECT", "UPDATE", "INSERT"]
  schema      = "source"
}


# Grand select,update,insert,usage staging for read_write

resource "postgresql_grant" "sta_read_write_schema_core_dev" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.sta_read_write.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "core"
}
resource "postgresql_grant" "sta_read_write_schema_analytics_dev" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.sta_read_write.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "analytics"
}
resource "postgresql_grant" "sta_read_write_schema_auth_dev" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.sta_read_write.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "auth"
}
resource "postgresql_grant" "sta_read_write_schema_source_dev" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.sta_read_write.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "source"
}
resource "postgresql_grant" "sta_read_write_schema_outbox_dev" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.sta_read_write.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "outbox"
}
resource "postgresql_grant" "sta_read_write_tables_core_dev" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.sta_read_write.name
  object_type = "table"
  privileges  = ["SELECT", "UPDATE", "INSERT"]
  schema      = "core"
}
resource "postgresql_grant" "sta_read_write_tables_analytics_dev" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.sta_read_write.name
  object_type = "table"
  privileges  = ["SELECT", "UPDATE", "INSERT"]
  schema      = "analytics"
}
resource "postgresql_grant" "sta_read_write_tables_auth_dev" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.sta_read_write.name
  object_type = "table"
  privileges  = ["SELECT", "UPDATE", "INSERT"]
  schema      = "auth"
}
resource "postgresql_grant" "sta_read_write_tables_source_dev" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.sta_read_write.name
  object_type = "table"
  privileges  = ["SELECT", "UPDATE", "INSERT"]
  schema      = "source"
}
resource "postgresql_grant" "sta_read_write_tables_outbox_dev" {
  provider    = postgresql.staging
  database    = yandex_mdb_postgresql_database.staging.name
  role        = yandex_mdb_postgresql_user.sta_read_write.name
  object_type = "table"
  privileges  = ["SELECT", "UPDATE", "INSERT"]
  schema      = "outbox"
}

# Grand select,update,insert,usage prod for read_write

resource "postgresql_grant" "pro_read_write_schema_core_dev" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.pro_read_write.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "core"
}
resource "postgresql_grant" "pro_read_write_schema_analytics_dev" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.pro_read_write.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "analytics"
}
resource "postgresql_grant" "pro_read_write_schema_auth_dev" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.pro_read_write.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "auth"
}
resource "postgresql_grant" "pro_read_write_schema_source_dev" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.pro_read_write.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "source"
}
resource "postgresql_grant" "pro_read_write_schema_outbox_dev" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.pro_read_write.name
  object_type = "schema"
  privileges  = ["USAGE"]
  schema      = "outbox"
}
resource "postgresql_grant" "pro_read_write_tables_core_dev" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.pro_read_write.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "core"
}
resource "postgresql_grant" "pro_read_write_tables_analytics_dev" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.pro_read_write.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "analytics"
}
resource "postgresql_grant" "pro_read_write_tables_auth_dev" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.pro_read_write.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "auth"
}
resource "postgresql_grant" "pro_read_write_tables_source_dev" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.pro_read_write.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "source"
}
resource "postgresql_grant" "pro_read_write_tables_outbox_dev" {
  database    = yandex_mdb_postgresql_database.production.name
  role        = yandex_mdb_postgresql_user.pro_read_write.name
  object_type = "table"
  privileges  = ["SELECT"]
  schema      = "outbox"
}
