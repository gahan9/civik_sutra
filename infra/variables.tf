variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run and Artifact Registry"
  type        = string
  default     = "asia-south1"
}

variable "image_tag_frontend" {
  description = "Docker image tag for the frontend service"
  type        = string
  default     = "latest"
}

variable "image_tag_api" {
  description = "Docker image tag for the API service"
  type        = string
  default     = "latest"
}
