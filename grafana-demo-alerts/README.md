# grafana-demo-alerts

疑似設備アラート監視システムの実装本体です。

## ディレクトリ構成

```
grafana-demo-alerts/
├── terraform/      Terraform 定義（AWS リソース）
├── lambda/         Lambda 関数ソース（handler.py）
├── samples/        疑似アラートサンプル JSON
└── docs/           手動設定手順（dashboard.md 等）
```

## 前提条件

- AWS CLI v2、IAM Identity Center (SSO) 認証済み
- Terraform >= 1.5
- Python 3.x（ローカルテスト用、デプロイは Terraform が ZIP 化）
- AWS リージョン: `ap-northeast-1`

## 構築手順

```bash
cd terraform

# AWS プロファイル設定（SSO セッションが切れたら aws sso login で再認証）
export AWS_PROFILE=<your-sso-profile>

# 初期化
terraform init

# 構文チェック・実行計画
terraform fmt
terraform validate
terraform plan

# 適用（リソース作成）
terraform apply
```

`apply` 完了後、`terraform output` で API エンドポイント等を確認できます。

## 動作確認

```bash
# API エンドポイント取得
API_ENDPOINT=$(terraform output -raw api_endpoint)

# 疑似アラート送信
curl -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d @../samples/alert-critical.json
```

期待レスポンス: `{"message": "alert accepted", "alertId": "ALT-0001", "stored": true}`

## Grafana ダッシュボード設定

ワークスペース作成後の手動設定手順は `docs/dashboard.md` を参照。

## 削除手順

```bash
cd terraform
terraform destroy
```

削除確認手順は `docs/cleanup.md` を参照。

## 作成される AWS リソース

| カテゴリ | リソース |
|---|---|
| API | API Gateway HTTP API、Stage、Route、Integration |
| 計算 | Lambda 関数（Python 3.12） |
| ストレージ | DynamoDB テーブル（PAY_PER_REQUEST） |
| ログ | CloudWatch Log Group（保持 3 日） |
| 可視化 | Amazon Managed Grafana Workspace |
| IAM | Lambda 実行ロール、Grafana 用ロール |

## Terraform 管理外（手動設定）

- Grafana CloudWatch Data Source 設定
- Grafana ダッシュボード作成（JSON エクスポートを `docs/dashboard-export.json` に保存）
- Grafana Alerting ルール（任意拡張）
