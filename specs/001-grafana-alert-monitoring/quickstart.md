# Quickstart: 疑似設備アラート監視システム

**Phase**: 1 — Design & Contracts  
**Date**: 2026-04-25  
**Feature**: [spec.md](./spec.md) | [plan.md](./plan.md)

このドキュメントは、検証環境の構築→動作確認→削除までの手順を整理したものです。  
検証時間の目安: **約 2 時間以内**

---

## 前提条件

- AWS CLI が設定済みであること（`aws configure` 完了）
- 使用するプロファイルに十分な権限があること（AdministratorAccess 推奨）
- Terraform >= 1.5 がインストールされていること
- curl が使用できること

---

## Phase 1: Terraform でリソース構築（目安: 15〜30 分）

### 1-1. リポジトリのクローン・移動

```bash
git clone <repository-url>
cd grafana-demo-alerts
```

### 1-2. Terraform 初期化

```bash
cd terraform
terraform init
```

### 1-3. フォーマット・検証

```bash
terraform fmt
terraform validate
```

### 1-4. 実行計画確認

```bash
terraform plan
```

作成されるリソース数・内容を確認する。意図しないリソースが含まれていないか確認。

### 1-5. リソース作成

```bash
terraform apply
```

`yes` と入力して実行。完了後、以下の出力値を確認・メモする：

```
Outputs:
api_endpoint         = "https://xxxxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/alerts"
lambda_function_name = "grafana-demo-alert-handler"
dynamodb_table_name  = "grafana-demo-alerts"
log_group_name       = "/aws/lambda/grafana-demo-alert-handler"
grafana_workspace_id = "g-xxxxxxxxxx"
grafana_endpoint     = "https://g-xxxxxxxxxx.grafana-workspace.ap-northeast-1.amazonaws.com"
```

---

## Phase 2: 疑似アラートの送信（目安: 5 分）

### 2-1. API エンドポイントの取得

```bash
API_ENDPOINT=$(terraform output -raw api_endpoint)
echo $API_ENDPOINT
```

### 2-2. サンプルデータの送信（critical）

```bash
curl -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d @../samples/alert-critical.json
```

**期待レスポンス**:
```json
{"message": "alert accepted", "alertId": "ALT-0001", "stored": true}
```

### 2-3. 複数件の送信（warning / info）

```bash
curl -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d @../samples/alert-warning.json

curl -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d @../samples/alert-info.json
```

### 2-4. エラーケースの確認

**severity 不正**:
```bash
curl -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{"alertId": "ERR-001", "facilityId": "FAC-001", "facilityName": "設備", "severity": "high", "alertType": "test", "message": "test", "occurredAt": "2026-04-25T10:00:00+09:00"}'
```
**期待レスポンス**: `HTTP 400` + `{"error": "INVALID_SEVERITY", ...}`

**必須フィールド欠損**:
```bash
curl -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{"alertId": "ERR-002"}'
```
**期待レスポンス**: `HTTP 400` + `{"error": "MISSING_FIELD", ...}`

---

## Phase 3: AWS コンソールでの確認（目安: 10 分）

### 3-1. DynamoDB 確認

1. AWS コンソール → DynamoDB → テーブル → `grafana-demo-alerts`
2. 「テーブルアイテムの探索」→ 送信したレコードが存在することを確認

### 3-2. CloudWatch Logs 確認

1. AWS コンソール → CloudWatch → ロググループ → `/aws/lambda/grafana-demo-alert-handler`
2. 最新のログストリームを開き、以下のログイベントを確認：
   - `REQUEST_RECEIVED`
   - `STORED`
   - エラーケースの場合は `VALIDATION_ERROR`

### 3-3. CloudWatch Metrics 確認

1. AWS コンソール → CloudWatch → メトリクス
2. 以下の名前空間でメトリクスを確認：
   - `AWS/ApiGateway` → `Count`, `4XXError`, `5XXError`, `Latency`
   - `AWS/Lambda` → `Invocations`, `Errors`, `Duration`
   - `AWS/DynamoDB` → `ConsumedWriteCapacityUnits`

---

## Phase 4: Grafana セットアップ（目安: 30〜45 分）

### 4-1. Grafana ワークスペースへのアクセス

1. AWS コンソール → Amazon Managed Grafana → ワークスペース
2. `grafana-demo-workspace` を選択
3. 「Grafana workspace URL」をクリック

### 4-2. 初回ログイン（組み込み認証）

1. Grafana 画面でユーザー名・パスワードを設定
2. Admin ユーザーとしてログイン

### 4-3. CloudWatch データソースの追加

1. 左メニュー → Connections → Data sources
2. 「Add data source」→ 「CloudWatch」を選択
3. 以下を設定：
   - **Authentication Provider**: `AWS SDK Default`（Grafana IAM ロールを自動使用）
   - **Default Region**: `ap-northeast-1`
4. 「Save & test」→ 「Data source is working」と表示されることを確認

### 4-4. ダッシュボードの作成

ダッシュボード作成の詳細手順は `docs/dashboard.md` を参照。

最小構成として以下のパネルを追加する：

| パネル名 | データソース | メトリクス |
|---|---|---|
| API リクエスト数 | CloudWatch | AWS/ApiGateway Count |
| API エラー数 | CloudWatch | AWS/ApiGateway 4XXError + 5XXError |
| Lambda 実行回数 | CloudWatch | AWS/Lambda Invocations |
| Lambda エラー数 | CloudWatch | AWS/Lambda Errors |
| DynamoDB 書き込み | CloudWatch | AWS/DynamoDB ConsumedWriteCapacityUnits |
| アラート総件数 | CloudWatch Logs | Logs Insights クエリ（下記参照） |
| severity 別件数 | CloudWatch Logs | Logs Insights クエリ（下記参照） |

### 4-5. Logs Insights クエリ例（Grafana パネル用）

**アラート総件数**:
```sql
fields @timestamp, @message
| filter event = "STORED"
| stats count() as total_alerts
```

**severity 別件数**:
```sql
fields @timestamp, @message
| filter event = "REQUEST_RECEIVED"
| stats count() by severity
```

**Lambda エラー確認**:
```sql
fields @timestamp, @message
| filter level = "ERROR"
| sort @timestamp desc
| limit 20
```

**アラート件数推移（5 分ごと）**:
```sql
fields @timestamp, @message
| filter event = "STORED"
| stats count() by bin(5m)
```

### 4-6. ダッシュボード JSON のエクスポート

1. ダッシュボード画面の右上 → 「Share」アイコン
2. 「Export」タブ → 「Save to file」
3. エクスポートした JSON を `docs/dashboard-export.json` として保存

---

## Phase 5: Grafana Alerting（任意、目安: 15 分）

P1〜P4 が完了した後に実施する。

### 5-1. アラートルールの作成例

1. 左メニュー → Alerting → Alert rules → 「New alert rule」
2. 以下のルールを作成：
   - **名前**: `Lambda Error Alert`
   - **条件**: `AWS/Lambda Errors > 0`（直近 5 分間）
   - **評価間隔**: 1 分

### 5-2. Firing 状態の確認

1. Lambda エラーを発生させるリクエストを送信（上記 2-4 参照）
2. Alerting 画面でルールが Firing 状態になることを確認

---

## Phase 6: 削除手順（目安: 10 分）

### 6-1. Terraform でリソース削除

```bash
cd grafana-demo-alerts/terraform
terraform destroy
```

`yes` と入力して実行。

### 6-2. 削除確認チェックリスト

以下の AWS コンソールでリソースが存在しないことを確認する：

| リソース | 確認場所 | 確認事項 |
|---|---|---|
| API Gateway | API Gateway → HTTP APIs | `grafana-demo-*` が存在しないこと |
| Lambda 関数 | Lambda → Functions | `grafana-demo-*` が存在しないこと |
| DynamoDB テーブル | DynamoDB → Tables | `grafana-demo-alerts` が存在しないこと |
| CloudWatch Logs | CloudWatch → Log groups | `/aws/lambda/grafana-demo-*` が存在しないこと |
| Grafana ワークスペース | Amazon Managed Grafana | ワークスペースが存在しないこと |
| IAM ロール | IAM → Roles | `grafana-demo-*` が存在しないこと |

### 6-3. 手動削除が必要な場合

`terraform destroy` で削除できなかったリソースがある場合は手動で削除する。  
詳細手順は `docs/cleanup.md` を参照。

### 6-4. Terraform state ファイルの削除

```bash
rm terraform/terraform.tfstate
rm terraform/terraform.tfstate.backup
rm -rf terraform/.terraform/
```

---

## トラブルシューティング

### API が 500 エラーを返す

- CloudWatch Logs でエラーログを確認する
- Lambda の実行ロールに DynamoDB の権限があるか確認する
- DynamoDB テーブルが存在するか確認する

### Grafana から CloudWatch に接続できない

- Grafana 用 IAM ロールに CloudWatch の参照権限があるか確認する
- データソース設定で Region が `ap-northeast-1` に設定されているか確認する

### Logs Insights クエリに結果が表示されない

- Lambda が実行されてから数分程度ラグがある場合がある
- ログフォーマットが JSON 形式になっているか確認する
- Grafana のクエリ時間範囲を調整する（デフォルト: 過去 1 時間）

### terraform apply が失敗する

- `terraform validate` で設定ファイルのエラーを確認する
- AWS CLI の認証情報が正しいか確認する（`aws sts get-caller-identity`）
- 必要な IAM 権限が付与されているか確認する
