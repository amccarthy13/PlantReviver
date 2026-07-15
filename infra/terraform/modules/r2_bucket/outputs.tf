output "bucket_name" {
  value       = cloudflare_r2_bucket.photos.name
  description = "Name of the R2 bucket."
}
