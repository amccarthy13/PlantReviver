variable "service_name" {
  type    = string
  default = "plantreviver"
}

variable "repo_url" {
  type        = string
  description = "GitHub repo URL Render deploys from."
}

variable "branch" {
  type    = string
  default = "main"
}

variable "cloudflare_account_id" {
  type = string
}

variable "jwt_secret" {
  type      = string
  sensitive = true
}
