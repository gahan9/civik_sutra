terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ---------------------------------------------------------------------------
# Artifact Registry
# ---------------------------------------------------------------------------

resource "google_artifact_registry_repository" "civiksutra" {
  location      = var.region
  repository_id = "civiksutra"
  description   = "Docker images for CivikSutra frontend and API"
  format        = "DOCKER"
}

# ---------------------------------------------------------------------------
# Cloud Run — Frontend (Nginx SPA)
# ---------------------------------------------------------------------------

resource "google_cloud_run_v2_service" "frontend" {
  name     = "civiksutra-frontend"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/civiksutra/frontend:${var.image_tag_frontend}"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "256Mi"
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# ---------------------------------------------------------------------------
# Cloud Run — API (FastAPI)
# ---------------------------------------------------------------------------

resource "google_cloud_run_v2_service" "api" {
  name     = "civiksutra-api"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/civiksutra/api:${var.image_tag_api}"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name  = "EP_GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "EP_CORS_ORIGINS"
        value = "[\"https://civiksutra-2604261729.web.app\"]"
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# ---------------------------------------------------------------------------
# IAM — Allow unauthenticated access (public facing)
# ---------------------------------------------------------------------------

resource "google_cloud_run_v2_service_iam_member" "frontend_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service_iam_member" "api_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
