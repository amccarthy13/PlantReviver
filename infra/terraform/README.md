# PlantReviver — Infrastructure (Terraform)

Declares all cloud infra so it's reproducible and reviewable. This is a
**learning goal**, not a necessity at this scale (see repo `ARCHITECTURE.md` §9).

> ⚠️ **Starter templates.** The resource attributes in `modules/` follow the
> `render-oss/render` and `cloudflare/cloudflare` providers but have **not** been
> validated against a live `terraform init`. Treat them as a scaffold: run
> `terraform init` in an environment dir, then reconcile each resource with the
> provider registry docs before your first `apply`.

## Layout

```
modules/
  render_service/   # Render web service + managed Postgres
  r2_bucket/        # Cloudflare R2 bucket
environments/
  staging/          # composes the modules for staging
  prod/             # composes the modules for prod
```

## State

Remote state in **HCP Terraform** (free tier) for locking + run history. Each
environment maps to its own workspace (`plantreviver-staging`, `plantreviver-prod`).
Set the `organization` in each environment's `main.tf`.

## Providers / credentials (never commit secrets)

- Render: `RENDER_API_KEY`
- Cloudflare: `CLOUDFLARE_API_TOKEN`, plus your account id as a variable.

## Usage

```bash
cd environments/staging
cp terraform.tfvars.example terraform.tfvars   # fill in, git-ignored
terraform init
terraform plan
terraform apply
```

## Deferred (add later without rearchitecture — ARCHITECTURE.md §1)

Background worker, cron job, and Redis ("Key Value") become additional resources
in `modules/render_service` (or a new module) when those features land.
