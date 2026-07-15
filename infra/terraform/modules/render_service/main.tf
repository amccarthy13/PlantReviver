terraform {
  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.4"
    }
  }
}

# NOTE: starter template — verify attributes against the provider docs
# (registry.terraform.io/providers/render-oss/render/latest/docs) before apply.

resource "render_postgres" "db" {
  name          = "${var.service_name}-db-${var.environment}"
  plan          = var.database_plan
  region        = var.region
  version       = "16"
  database_name = "plantreviver"
  database_user = "plantreviver"
}

resource "render_web_service" "api" {
  name   = "${var.service_name}-${var.environment}"
  region = var.region
  plan   = var.service_plan

  runtime_source = {
    docker = {
      repo_url        = var.repo_url
      branch          = var.branch
      dockerfile_path = "backend/Dockerfile"
      context         = "backend"
    }
  }

  env_vars = {
    ENVIRONMENT  = { value = var.environment }
    DATABASE_URL = { value = render_postgres.db.connection_info.internal_connection_string }
    JWT_SECRET   = { value = var.jwt_secret }
  }
}
