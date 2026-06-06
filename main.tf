terraform {
  backend "gcs" {
    bucket = "tf-state-gen-lang-client-0111574187"
    prefix = "terraform/state"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# ──────────────────────────────────────────────
# Variables
# ──────────────────────────────────────────────

variable "project_id" {
  description = "The GCP project ID to deploy to"
  type        = string
  default     = "gen-lang-client-0111574187"
}

variable "region" {
  description = "The GCP region for all resources"
  type        = string
  default     = "us-central1"
}

variable "image_tag" {
  description = "The Docker image tag to deploy"
  type        = string
  default     = "latest"
}

# ──────────────────────────────────────────────
# Provider
# ──────────────────────────────────────────────

provider "google" {
  project = var.project_id
  region  = var.region
}

# ──────────────────────────────────────────────
# Artifact Registry
# ──────────────────────────────────────────────

resource "google_artifact_registry_repository" "my_repo" {
  location      = var.region
  repository_id = "my-free-site-repo"
  description   = "Docker repository for my free site"
  format        = "DOCKER"
}

# ──────────────────────────────────────────────
# Cloud Run Service
# ──────────────────────────────────────────────

resource "google_cloud_run_v2_service" "my_free_site" {
  name     = "my-free-site"
  location = var.region

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }
    containers {
      image = "${google_artifact_registry_repository.my_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.my_repo.repository_id}/my-free-site:${var.image_tag}"
      resources {
        limits = {
          cpu    = "1"
          memory = "256Mi"
        }
        cpu_idle = true
      }

      # Health check using the dedicated endpoint
      startup_probe {
        http_get {
          path = "/health"
        }
        initial_delay_seconds = 0
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
        }
        period_seconds = 30
      }
    }
  }

  lifecycle {
    ignore_changes = [
      client,
      client_version,
      template[0].revision,
      labels,
      annotations
    ]
  }
}

# ──────────────────────────────────────────────
# IAM — Public Access
# ──────────────────────────────────────────────

resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.my_free_site.name
  location = google_cloud_run_v2_service.my_free_site.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ──────────────────────────────────────────────
# Outputs
# ──────────────────────────────────────────────

output "service_url" {
  description = "The URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.my_free_site.uri
}

output "artifact_registry_url" {
  description = "The Artifact Registry Docker repository URL"
  value       = "${google_artifact_registry_repository.my_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.my_repo.repository_id}"
}
