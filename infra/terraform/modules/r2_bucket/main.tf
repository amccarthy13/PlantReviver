terraform {
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.40"
    }
  }
}

# NOTE: starter template — verify against the Cloudflare provider docs before apply.
resource "cloudflare_r2_bucket" "photos" {
  account_id = var.cloudflare_account_id
  name       = var.bucket_name
  location   = var.location
}

# TODO: lifecycle rule to expire orphaned/incomplete uploads (ARCHITECTURE.md §9).
