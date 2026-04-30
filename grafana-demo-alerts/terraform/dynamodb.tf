resource "aws_dynamodb_table" "alerts" {
  name         = local.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "alertId"

  attribute {
    name = "alertId"
    type = "S"
  }
}
