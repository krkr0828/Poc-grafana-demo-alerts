resource "aws_grafana_workspace" "main" {
  name                     = local.workspace_name
  description              = "疑似設備アラート監視ダッシュボード"
  account_access_type      = "CURRENT_ACCOUNT"
  authentication_providers = ["AWS_SSO"]
  permission_type          = "SERVICE_MANAGED"
  role_arn                 = aws_iam_role.grafana.arn
  data_sources             = ["CLOUDWATCH"]
}
