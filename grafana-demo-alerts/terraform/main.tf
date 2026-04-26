locals {
  common_tags = {
    Project     = var.project_name
    Environment = "dev"
    ManagedBy   = "terraform"
  }

  table_name     = "${var.project_name}-alerts"
  lambda_name    = "${var.project_name}-alert-handler"
  log_group_name = "/aws/lambda/${var.project_name}-alert-handler"
  api_name       = "${var.project_name}-api"
  workspace_name = "${var.project_name}-workspace"
}
