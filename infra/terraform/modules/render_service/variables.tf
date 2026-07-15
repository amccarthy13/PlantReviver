variable "environment" {
  type        = string
  description = "Deployment environment (staging|prod)."
}

variable "service_name" {
  type        = string
  default     = "plantreviver"
  description = "Base name for Render resources."
}

variable "region" {
  type        = string
  default     = "oregon"
  description = "Render region."
}

variable "service_plan" {
  type        = string
  default     = "starter"
  description = "Render web service plan."
}

variable "database_plan" {
  type        = string
  default     = "basic_256mb"
  description = "Render managed Postgres plan."
}

variable "repo_url" {
  type        = string
  description = "GitHub repo URL Render deploys from."
}

variable "branch" {
  type        = string
  default     = "main"
  description = "Branch Render deploys."
}

variable "jwt_secret" {
  type        = string
  sensitive   = true
  description = "App JWT signing secret."
}
