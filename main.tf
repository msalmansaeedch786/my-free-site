terraform {
  backend "gcs" {
    bucket  = "tf-state-gen-lang-client-0111574187"
    prefix  = "terraform/state"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "gen-lang-client-0111574187"
  region  = "us-central1"
}

variable "image_tag" {
  description = "The Docker image tag to deploy"
  type        = string
  default     = "latest"
}

resource "google_artifact_registry_repository" "my_repo" {
  location      = "us-central1"
  repository_id = "my-free-site-repo"
  description   = "Docker repository for my free site"
  format        = "DOCKER"
}

resource "google_cloud_run_v2_service" "my_free_site" {
  name     = "my-free-site"
  location = "us-central1"

  template {
    scaling {
      max_instance_count = 1
    }
    containers {
      image = "${google_artifact_registry_repository.my_repo.location}-docker.pkg.dev/gen-lang-client-0111574187/${google_artifact_registry_repository.my_repo.repository_id}/my-free-site:${var.image_tag}"
      resources {
        limits = {
          cpu    = "1"
          memory = "256Mi"
        }
        cpu_idle = true
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

resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.my_free_site.name
  location = google_cloud_run_v2_service.my_free_site.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
