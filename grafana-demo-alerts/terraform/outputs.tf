output "api_endpoint" {
  description = "疑似アラート受信 API のエンドポイント URL（/alerts パス付き）"
  value       = "${aws_apigatewayv2_api.main.api_endpoint}/alerts"
}

output "lambda_function_name" {
  description = "Lambda 関数名"
  value       = aws_lambda_function.alert_handler.function_name
}

output "dynamodb_table_name" {
  description = "DynamoDB テーブル名"
  value       = aws_dynamodb_table.alerts.name
}

output "log_group_name" {
  description = "Lambda の CloudWatch ロググループ名"
  value       = aws_cloudwatch_log_group.lambda.name
}

output "grafana_workspace_id" {
  description = "Amazon Managed Grafana ワークスペース ID"
  value       = aws_grafana_workspace.main.id
}

output "grafana_endpoint" {
  description = "Grafana ワークスペースアクセス URL"
  value       = "https://${aws_grafana_workspace.main.endpoint}"
}
