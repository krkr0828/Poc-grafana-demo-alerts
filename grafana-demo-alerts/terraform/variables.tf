variable "aws_region" {
  description = "AWS リージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "project_name" {
  description = "プロジェクト名（リソース命名のプレフィックス）"
  type        = string
  default     = "grafana-demo"
}

variable "log_retention_days" {
  description = "CloudWatch Logs の保持期間（日）"
  type        = number
  default     = 3
}

variable "lambda_memory_size" {
  description = "Lambda 関数のメモリサイズ (MB)"
  type        = number
  default     = 128
}

variable "lambda_timeout" {
  description = "Lambda 関数のタイムアウト（秒）"
  type        = number
  default     = 10
}
