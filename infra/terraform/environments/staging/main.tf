terraform {
  required_version = ">= 1.9"

  # Remote state in HCP Terraform (free tier). Set your org below.
  cloud {
    organization = "REPLACE_WITH_HCP_ORG"
    workspaces {
      name = "plantreviver-staging"
    }
  }

  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.4"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.40"
    }
  }
}

# Credentials come from env vars: RENDER_API_KEY, CLOUDFLARE_API_TOKEN.
provider "render" {}
provider "cloudflare" {}

module "render" {
  source       = "../../modules/render_service"
  environment  = "staging"
  service_name = var.service_name
  repo_url     = var.repo_url
  branch       = var.branch
  jwt_secret   = var.jwt_secret
}

module "r2" {
  source                = "../../modules/r2_bucket"
  cloudflare_account_id = var.cloudflare_account_id
  bucket_name           = "${var.service_name}-photos-staging"
}

output "api_url" {
  value = module.render.service_url
}
