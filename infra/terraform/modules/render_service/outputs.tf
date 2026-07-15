output "service_url" {
  value       = render_web_service.api.url
  description = "Public URL of the deployed API."
}

output "postgres_id" {
  value       = render_postgres.db.id
  description = "Render Postgres instance id."
}
