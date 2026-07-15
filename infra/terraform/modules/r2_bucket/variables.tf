variable "cloudflare_account_id" {
  type        = string
  description = "Cloudflare account id that owns the R2 bucket."
}

variable "bucket_name" {
  type        = string
  description = "R2 bucket name."
}

variable "location" {
  type        = string
  default     = "wnam"
  description = "R2 bucket location hint (e.g. wnam, enam, weur)."
}
