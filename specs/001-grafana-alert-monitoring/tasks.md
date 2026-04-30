# Tasks: 疑似設備アラート監視システム

**Input**: `specs/001-grafana-alert-monitoring/`  
**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md) | **Date**: 2026-04-25

---

## 1. はじめに

本タスク書は「疑似設備アラート監視システム」の実装作業を Claude Code に依頼するための作業指示書です。  
各タスクは 15〜45 分程度で完了できる粒度に分解されています。

---

## 2. 作業方針

- 最小構成で動作確認することを最優先にする
- 本番品質の過剰な作り込みはしない（認証・WAF・マルチAZ等は対象外）
- AWSリソースは原則 Terraform で作成・管理する
- Terraform state は local backend を使用する（S3 等は不要）
- コスト増につながるカスタムメトリクスや高頻度実行は避ける
- ログは JSON 構造化ログ形式で出力する
- リソース名は `grafana-demo-` プレフィックスで統一する
- 不明点があれば最小構成で実装し、任意拡張は後回しにする

---

## 3. 前提条件

- AWS CLI が設定済みであること（`aws configure` / 必要な IAM 権限あり）
- Terraform >= 1.5 がインストールされていること
- Python 3.x がインストールされていること（Lambda ソースの編集用）
- curl が使用できること（API 動作確認用）
- AWSリージョン: `ap-northeast-1`（東京）

---

## 4. 作業全体フロー

```
Phase 1: 事前準備
  ↓
Phase 2: Terraform プロジェクト作成
  ↓
Phase 3: Lambda 実装
  ↓
Phase 4: Terraform による AWS リソース定義
  ↓
Phase 5: Terraform 実行（リソース作成）
  ↓
Phase 6: API 動作確認 ←── US1 完了
  ↓
Phase 7: CloudWatch 確認 ←── US1 完了
  ↓
Phase 8: Amazon Managed Grafana 設定 ←── US2 開始
  ↓
Phase 9: Grafana ダッシュボード作成 ←── US2 完了
  ↓
Phase 10: テスト（正常系・異常系・可視化）
  ↓
Phase 11: 削除作業 ←── US4 完了
```

---

## 5. タスク一覧（チェックリスト）

### Phase 1: 事前準備

- [ ] T001 作業ディレクトリ作成（`grafana-demo-alerts/`）
- [ ] T002 リポジトリ初期化・`.gitignore` 作成
- [ ] T003 README 初期版作成（`README.md`）
- [ ] T004 前提条件確認（AWS CLI 認証・Terraform バージョン確認）

### Phase 2: Terraform プロジェクト作成

- [ ] T005 Terraform ファイル構成作成（`terraform/` ディレクトリ）
- [ ] T006 [P] `providers.tf` 定義（AWS provider 設定）
- [ ] T007 [P] `variables.tf` / `main.tf` 定義（変数・common tags）
- [ ] T008 `outputs.tf` 定義（API URL 等の出力値）
- [ ] T009 [P] サンプルデータ JSON 作成（`samples/`）

### Phase 3: Lambda 実装

- [ ] T010 [US1] `lambda/handler.py` - リクエスト受信・JSON パース・入力チェック処理実装
- [ ] T011 [US1] `lambda/handler.py` - DynamoDB 保存処理・upsert 動作実装
- [ ] T012 [US1] `lambda/handler.py` - ログ出力（JSON 構造化）・例外処理実装

### Phase 4: Terraform AWS リソース定義

- [ ] T013 [US1] `terraform/dynamodb.tf` - DynamoDB テーブル定義
- [ ] T014 [US1] `terraform/iam.tf` - Lambda 実行ロール・IAM ポリシー定義
- [ ] T015 [US1] `terraform/cloudwatch.tf` - Lambda ロググループ・保持期間定義
- [ ] T016 [US1] `terraform/lambda.tf` - Lambda 関数定義（ZIP パッケージング込み）
- [ ] T017 [US1] `terraform/apigateway.tf` - API Gateway HTTP API・route・integration 定義
- [ ] T018 [US2] `terraform/grafana.tf` - Managed Grafana Workspace 定義
- [ ] T019 [US2] `terraform/iam.tf` 追記 - Grafana 用 IAM ロール・ポリシー定義

### Phase 5: Terraform 実行

- [ ] T020 `terraform init` / `fmt` / `validate` / `plan` 実行・確認
- [ ] T021 `terraform apply` 実行・出力値確認

### Phase 6: API 動作確認（US1）

- [ ] T022 [US1] 正常系リクエスト送信（critical / warning / info 各 1 件）
- [ ] T023 [US1] 異常系リクエスト送信（4 種類のエラーケース確認）
- [ ] T024 [US1] DynamoDB コンソールでのデータ保存確認

### Phase 7: CloudWatch 確認（US1）

- [ ] T025 [US1] CloudWatch Logs でラムダ処理ログ確認
- [ ] T026 [US1] CloudWatch Metrics で各サービスメトリクス確認
- [ ] T027 [US1] Logs Insights クエリ動作確認（3 クエリ）

### Phase 8: Amazon Managed Grafana 設定（US2）

- [ ] T028 [US2] Grafana 初回ログイン・Admin ユーザー設定
- [ ] T029 [US2] CloudWatch Data Source 設定・接続確認

### Phase 9: Grafana ダッシュボード作成（US2）

- [ ] T030 [US2] 必須パネル作成（API Gateway / Lambda / DynamoDB メトリクス 6 パネル）
- [ ] T031 [US2] アラート件数パネル作成（Logs Insights 2 パネル）
- [ ] T032 [US2] ダッシュボード JSON エクスポート・`docs/dashboard.md` 作成

### Phase 10: テスト

- [ ] T033 [US1][US2] 正常系・異常系・可視化の統合テスト実施
- [ ] T034 Terraform コマンド一連確認（fmt / validate / plan / apply）

### Phase 11: 削除作業（US4）

- [ ] T035 [US4] `terraform destroy` 実行
- [ ] T036 [US4] AWS コンソールで削除漏れ確認
- [ ] T037 [US4] ローカルの state ファイル・一時ファイル整理

---

## 6. Phase 1: 事前準備

---

### TASK-001: 作業ディレクトリ作成

#### 区分
- 必須

#### 目的
- 実装作業のベースとなるディレクトリ構造を作成する

#### 作業内容
- 以下のディレクトリ・ファイル構成を作成する

```text
grafana-demo-alerts/
├── terraform/
├── lambda/
├── samples/
└── docs/
```

#### 作成・変更対象
- `grafana-demo-alerts/` ディレクトリ（リポジトリルート）
- `terraform/`、`lambda/`、`samples/`、`docs/` の各サブディレクトリ

#### 前提条件
- 作業マシンに書き込み権限があること

#### 完了条件
- 上記ディレクトリ構造が作成されていること

#### 確認方法
- `ls -la grafana-demo-alerts/` でディレクトリ構造を確認

#### 依存タスク
- なし

#### 注意点
- リポジトリルートに `grafana-demo-alerts/` として作成すること
- 既存プロジェクトディレクトリがある場合は上書きしないこと

---

### TASK-002: リポジトリ初期化・`.gitignore` 作成

#### 区分
- 必須

#### 目的
- Git リポジトリとして初期化し、不要ファイルの追跡を防ぐ

#### 作業内容
- `grafana-demo-alerts/` で `git init` を実行する
- `.gitignore` を作成し、以下を含める：
  - Terraform: `.terraform/`、`*.tfstate`、`*.tfstate.backup`、`*.tfvars`
  - Python: `__pycache__/`、`*.pyc`、`*.zip`
  - OS: `.DS_Store`、`Thumbs.db`
  - その他: `*.log`

#### 作成・変更対象
- `grafana-demo-alerts/.gitignore`

#### 前提条件
- TASK-001 完了

#### 完了条件
- `.gitignore` が存在し、Terraform state ファイルが対象に含まれていること

#### 確認方法
- `cat grafana-demo-alerts/.gitignore` で内容確認

#### 依存タスク
- TASK-001

#### 注意点
- `*.tfstate` は機密情報（ARN 等）を含む場合があるため、必ず `.gitignore` に含めること
- `terraform.tfvars` も `.gitignore` に含めること

---

### TASK-003: README 初期版作成

#### 区分
- 必須

#### 目的
- システム概要・構築手順・削除手順の基本情報を記録する

#### 作業内容
- `README.md` に以下のセクションを作成する：
  - システム概要（1 段落）
  - 前提条件（AWS CLI / Terraform バージョン要件）
  - ディレクトリ構成
  - 構築手順（terraform apply まで）
  - 動作確認手順（curl コマンド例）
  - 削除手順（terraform destroy）
  - 手動設定が必要な箇所（Grafana 設定）
  - 作成 AWS リソース一覧

#### 作成・変更対象
- `grafana-demo-alerts/README.md`

#### 前提条件
- TASK-001 完了

#### 完了条件
- 上記セクションが含まれた README.md が存在すること
- 後続タスクで内容を随時更新する前提でよい（完成品でなくてよい）

#### 確認方法
- `cat grafana-demo-alerts/README.md` で内容確認

#### 依存タスク
- TASK-001

#### 注意点
- 実装完了後に最終版へ更新すること（TASK-033 で確認）

---

### TASK-004: 前提条件確認（AWS CLI・Terraform）

#### 区分
- 必須

#### 目的
- 実装に必要なツールと認証情報が正しく設定されていることを確認する

#### 作業内容
- 以下のコマンドを実行し、それぞれの出力を確認する：

```bash
# AWS CLI 認証確認
aws sts get-caller-identity

# リージョン確認
aws configure get region

# Terraform バージョン確認
terraform version

# 作業リージョンの確認（ap-northeast-1 であること）
aws ec2 describe-regions --query "Regions[?RegionName=='ap-northeast-1']"
```

#### 作成・変更対象
- なし（確認のみ）

#### 前提条件
- AWS CLI がインストール・設定済みであること
- Terraform がインストール済みであること

#### 完了条件
- `aws sts get-caller-identity` が成功すること
- `terraform version` が 1.5 以上であること
- デフォルトリージョンが `ap-northeast-1` に設定されていること（または後続の variables.tf で明示指定する）

#### 確認方法
- 各コマンドの出力を目視確認

#### 依存タスク
- TASK-001

#### 注意点
- ルートアカウントを使用しないこと
- 必要な IAM 権限が付与されたユーザー/ロールで操作すること

---

## 7. Phase 2: Terraform プロジェクト作成

---

### TASK-005: Terraform ファイル構成作成

#### 区分
- 必須

#### 目的
- Terraform 管理の AWS リソース定義用ファイルを作成し、プロジェクト構造を確立する

#### 作業内容
- `terraform/` 配下に以下の空ファイルを作成する：

```text
terraform/
├── providers.tf
├── variables.tf
├── outputs.tf
├── main.tf
├── iam.tf
├── lambda.tf
├── apigateway.tf
├── dynamodb.tf
├── grafana.tf
└── cloudwatch.tf
```

#### 作成・変更対象
- `grafana-demo-alerts/terraform/` 配下の各 `.tf` ファイル（空ファイルとして作成）

#### 前提条件
- TASK-001 完了

#### 完了条件
- `terraform/` 配下に 10 個の `.tf` ファイルが存在すること

#### 確認方法
- `ls grafana-demo-alerts/terraform/` で確認

#### 依存タスク
- TASK-001

#### 注意点
- `terraform.tfstate` は `.gitignore` に含まれていることを確認すること（TASK-002 参照）

---

### TASK-006: `providers.tf` 定義

#### 区分
- 必須

#### 目的
- AWS provider と Terraform の required_providers を設定する

#### 作業内容
- `terraform/providers.tf` に以下を定義する：
  - `terraform` ブロック：`required_version >= "1.5.0"`、`required_providers`（aws ~> 5.0、archive ~> 2.0）
  - `provider "aws"` ブロック：`region = var.aws_region`、default_tags で common tags を設定

```hcl
# 定義すべき内容のイメージ
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
  # backend: local（デフォルト。S3等は使用しない）
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = local.common_tags
  }
}
```

#### 作成・変更対象
- `grafana-demo-alerts/terraform/providers.tf`

#### 前提条件
- TASK-005 完了

#### 完了条件
- `terraform init` が成功すること

#### 確認方法
- `cd terraform && terraform init` を実行し、エラーがないことを確認

#### 依存タスク
- TASK-005

#### 注意点
- backend は local のまま（S3 remote backend は使用しない）
- archive provider は Lambda の ZIP パッケージング（`data.archive_file`）に使用する

---

### TASK-007: `variables.tf` / `main.tf` 定義

#### 区分
- 必須

#### 目的
- 変数と共通タグを定義し、全リソースで一貫した設定を可能にする

#### 作業内容

**`variables.tf`** に以下の変数を定義する：

| 変数名 | デフォルト値 | 説明 |
|---|---|---|
| `aws_region` | `"ap-northeast-1"` | AWSリージョン |
| `project_name` | `"grafana-demo"` | プロジェクト名（命名プレフィックス） |
| `log_retention_days` | `3` | CloudWatch Logs 保持期間（日） |
| `lambda_memory_size` | `128` | Lambda メモリ (MB) |
| `lambda_timeout` | `10` | Lambda タイムアウト（秒） |

**`main.tf`** に以下を定義する：

```hcl
locals {
  common_tags = {
    Project     = var.project_name
    Environment = "dev"
    ManagedBy   = "terraform"
  }
  table_name      = "${var.project_name}-alerts"
  lambda_name     = "${var.project_name}-alert-handler"
  log_group_name  = "/aws/lambda/${local.lambda_name}"
}
```

#### 作成・変更対象
- `grafana-demo-alerts/terraform/variables.tf`
- `grafana-demo-alerts/terraform/main.tf`

#### 前提条件
- TASK-006 完了

#### 完了条件
- `terraform validate` が成功すること（この時点での部分的な定義で可）

#### 確認方法
- `cd terraform && terraform validate`

#### 依存タスク
- TASK-006

#### 注意点
- `project_name` の変更でリソース名が一括変更されるように設計する
- 命名: `${var.project_name}-alerts` = `grafana-demo-alerts`

---

### TASK-008: `outputs.tf` 定義

#### 区分
- 必須

#### 目的
- `terraform apply` 後に必要な接続情報を出力できるようにする

#### 作業内容
- `terraform/outputs.tf` に以下の出力値を定義する：

| output 名 | 内容 |
|---|---|
| `api_endpoint` | API Gateway の完全エンドポイント URL（`/alerts` パス付き） |
| `lambda_function_name` | Lambda 関数名 |
| `dynamodb_table_name` | DynamoDB テーブル名 |
| `log_group_name` | CloudWatch ロググループ名 |
| `grafana_workspace_id` | Grafana Workspace ID |
| `grafana_endpoint` | Grafana アクセス URL |

#### 作成・変更対象
- `grafana-demo-alerts/terraform/outputs.tf`

#### 前提条件
- TASK-007 完了
- 後続の各リソース定義タスク完了後に参照先が解決される

#### 完了条件
- `terraform apply` 後に全 output 値が表示されること

#### 確認方法
- `terraform output` で全値が表示されることを確認

#### 依存タスク
- TASK-007（後続リソース定義タスクで参照先を追加していく）

#### 注意点
- API エンドポイントは `${aws_apigatewayv2_api.main.api_endpoint}/alerts` の形式で出力する
- `terraform output -raw api_endpoint` で curl から直接参照できるようにする

---

### TASK-009: サンプルデータ JSON 作成

#### 区分
- 必須

#### 目的
- API 動作確認・テストで使用する疑似アラートデータを用意する

#### 作業内容
- `samples/alert-critical.json` を作成する：

```json
{
  "alertId": "ALT-0001",
  "facilityId": "FAC-001",
  "facilityName": "第一変電所",
  "severity": "critical",
  "alertType": "temperature_high",
  "message": "温度上昇を検知しました",
  "occurredAt": "2026-04-25T10:00:00+09:00"
}
```

- `samples/alert-warning.json` を作成する：

```json
{
  "alertId": "ALT-0002",
  "facilityId": "FAC-002",
  "facilityName": "第二変電所",
  "severity": "warning",
  "alertType": "voltage_drop",
  "message": "電圧低下を検知しました",
  "occurredAt": "2026-04-25T10:05:00+09:00"
}
```

- `samples/alert-info.json` を作成する：

```json
{
  "alertId": "ALT-0003",
  "facilityId": "FAC-003",
  "facilityName": "第三変電所",
  "severity": "info",
  "alertType": "status_change",
  "message": "設備状態の変更を検知しました",
  "occurredAt": "2026-04-25T10:10:00+09:00"
}
```

#### 作成・変更対象
- `grafana-demo-alerts/samples/alert-critical.json`
- `grafana-demo-alerts/samples/alert-warning.json`
- `grafana-demo-alerts/samples/alert-info.json`

#### 前提条件
- TASK-001 完了

#### 完了条件
- 3 ファイルが存在し、有効な JSON であること

#### 確認方法
- `cat samples/alert-critical.json | python3 -m json.tool` で JSON バリデーション

#### 依存タスク
- TASK-001

#### 注意点
- 実データ・個人情報を含めないこと
- `occurredAt` は ISO 8601 形式（`+09:00` タイムゾーン含む）であること

---

## 8. Phase 3: Lambda 実装

---

### TASK-010: `handler.py` - リクエスト受信・入力チェック実装

#### 区分
- 必須（US1）

#### 目的
- API Gateway から受け取ったリクエストを検証し、不正なリクエストに対して適切なエラーレスポンスを返す

#### 作業内容
- `lambda/handler.py` を作成し、以下を実装する：
  1. `lambda_handler(event, context)` エントリーポイント定義
  2. 環境変数 `TABLE_NAME`、`LOG_LEVEL` の読み込み
  3. リクエストボディの取得（`event.get("body")`）
  4. 空ボディチェック（`HTTP 400` + `{"error": "EMPTY_BODY", ...}`）
  5. JSON パース処理（`json.loads()`、失敗時 `HTTP 400` + `{"error": "INVALID_JSON", ...}`）
  6. 必須フィールドチェック（7 フィールド全て）（失敗時 `HTTP 400` + `{"error": "MISSING_FIELD", ...}`）
  7. `severity` バリデーション（`critical`/`warning`/`info` 以外 → `HTTP 400` + `{"error": "INVALID_SEVERITY", ...}`）
  8. `occurredAt` フォーマットチェック（`datetime.fromisoformat()` で検証）（失敗時 `HTTP 400` + `{"error": "INVALID_DATE_FORMAT", ...}`）
  9. `_make_response(status_code, body_dict)` ヘルパー関数定義

#### 作成・変更対象
- `grafana-demo-alerts/lambda/handler.py`（新規作成）

#### 前提条件
- TASK-005 完了（`lambda/` ディレクトリ存在）

#### 完了条件
- 必須フィールド欠損リクエストに対して HTTP 400 が返ること（ローカルテスト可）
- severity 不正値に対して HTTP 400 が返ること
- 正常ボディを渡した場合にバリデーションが通過すること

#### 確認方法
- `python3 -c "import handler; print('import OK')"` でモジュール読み込みを確認
- TASK-021 の curl テストで実際のレスポンスを確認

#### 依存タスク
- TASK-009（サンプルデータでテスト可能）

#### 注意点
- 必須フィールドは `["alertId", "facilityId", "facilityName", "severity", "alertType", "message", "occurredAt"]` の 7 つ
- エラーレスポンスの形式: `{"error": "ERROR_CODE", "message": "説明文"}`（contracts/api.md 参照）
- `datetime.fromisoformat()` は Python 3.7+ で `+09:00` タイムゾーン付き文字列をサポートする

---

### TASK-011: `handler.py` - DynamoDB 保存処理・upsert 動作実装

#### 区分
- 必須（US1）

#### 目的
- バリデーション通過後のアラートデータを DynamoDB に保存する

#### 作業内容
- TASK-010 の `handler.py` に以下を追記する：
  1. boto3 DynamoDB リソース初期化（`boto3.resource("dynamodb")` / `table = dynamodb.Table(TABLE_NAME)`）
  2. `receivedAt` の付与（`datetime.utcnow().isoformat() + "Z"`）
  3. `source` 固定値（`"api"`）の付与
  4. `status` 固定値（`"open"`）の付与
  5. 重複 alertId チェック（事前に `get_item` で確認、存在する場合 WARN ログ出力）
  6. `table.put_item(Item=data)` による upsert 保存
  7. 正常レスポンス生成（`HTTP 200` + `{"message": "alert accepted", "alertId": ..., "stored": true}`）
  8. `ClientError` キャッチによる保存失敗時の `HTTP 500` + `{"error": "STORE_ERROR", ...}` レスポンス

#### 作成・変更対象
- `grafana-demo-alerts/lambda/handler.py`（TASK-010 に追記）

#### 前提条件
- TASK-010 完了

#### 完了条件
- 正常なリクエストデータを渡した場合に DynamoDB 保存まで到達するコードが完成していること

#### 確認方法
- TASK-021 の curl テストで `"stored": true` が返ることを確認
- TASK-024 の DynamoDB コンソール確認で実際のレコードを確認

#### 依存タスク
- TASK-010

#### 注意点
- `boto3.resource()` はモジュールレベル（`lambda_handler` の外）で初期化すること（Lambda の実行効率化）
- 重複 alertId は upsert（上書き更新）とする。エラーではなく WARN ログのみ出力する
- `put_item` に条件式（`condition_expression`）は付けないこと（upsert のため）

---

### TASK-012: `handler.py` - JSON 構造化ログ・例外処理実装

#### 区分
- 必須（US1）

#### 目的
- CloudWatch Logs に JSON 形式の構造化ログを出力し、Logs Insights での集計を可能にする

#### 作業内容
- TASK-011 の `handler.py` に以下を追記・修正する：
  1. `_log(level, event, alert_id, message, **extra)` ヘルパー関数実装
     - `json.dumps({"level": level, "event": event, "alertId": alert_id, "message": message, **extra})` を `print()` で出力
  2. 各処理ポイントでのログ出力追加：
     - 処理開始時: `INFO` / `REQUEST_RECEIVED` / alertId / `"Request received"`
     - バリデーション成功時: `INFO` / `VALIDATION_OK`
     - DynamoDB 保存成功時: `INFO` / `STORED`
     - alertId 重複時: `WARN` / `DUPLICATE_ALERT_ID`
     - バリデーションエラー時: `WARN` / `VALIDATION_ERROR` / field・value 含む
     - 保存失敗時: `ERROR` / `STORE_ERROR` / error_code 含む
     - 予期しない例外時: `ERROR` / `UNEXPECTED_ERROR`
  3. 最外部の `except Exception as e:` ブロック追加
     - `HTTP 500` + `{"error": "INTERNAL_ERROR", ...}` レスポンス
     - ログに `str(e)` のみ出力（スタックトレースはログに含める。ただし機密情報は含めない）

#### 作成・変更対象
- `grafana-demo-alerts/lambda/handler.py`（TASK-011 に追記・修正）

#### 前提条件
- TASK-011 完了

#### 完了条件
- `handler.py` 単体が Python 構文エラーなしで読み込めること
- ログ出力が JSON 形式であること（`print(json.dumps({...}))` 形式）

#### 確認方法
- `python3 -c "import lambda.handler"` でエラーなしを確認
- TASK-025 の CloudWatch Logs 確認で JSON ログが出力されることを確認

#### 依存タスク
- TASK-011

#### 注意点
- `print()` は Lambda の stdout → CloudWatch Logs に自動転送される
- ログにリクエストボディ全体を含めないこと（機密情報混入防止）
- `alert_id` が不明な場合（JSON パース前エラー）は `None` を渡す

---

## 9. Phase 4: Terraform による AWS リソース定義

---

### TASK-013: `dynamodb.tf` - DynamoDB テーブル定義

#### 区分
- 必須（US1）

#### 目的
- アラートデータを保存する DynamoDB テーブルを Terraform で定義する

#### 作業内容
- `terraform/dynamodb.tf` に `aws_dynamodb_table` リソースを定義する：
  - `name`: `local.table_name`（= `grafana-demo-alerts`）
  - `billing_mode`: `"PAY_PER_REQUEST"`
  - `hash_key`: `"alertId"`
  - `attribute`: `name = "alertId"`, `type = "S"`
  - TTL は設定しない（今回のスコープ外）
  - GSI は設定しない

#### 作成・変更対象
- `grafana-demo-alerts/terraform/dynamodb.tf`

#### 前提条件
- TASK-007 完了（`local.table_name` 参照のため）

#### 完了条件
- `terraform validate` が成功すること

#### 確認方法
- `terraform validate` でエラーなし
- `terraform plan` で DynamoDB テーブル作成が計画されること

#### 依存タスク
- TASK-007

#### 注意点
- `billing_mode = "PAY_PER_REQUEST"` を必ず指定すること（デフォルトはプロビジョンドで課金が発生する）
- 属性定義（`attribute` ブロック）はキーとして使用する属性のみ定義する（DynamoDB の仕様）

---

### TASK-014: `iam.tf` - Lambda 実行ロール・IAM ポリシー定義

#### 区分
- 必須（US1）

#### 目的
- Lambda が DynamoDB への書き込みと CloudWatch Logs への出力を行うための最小権限 IAM ロールを定義する

#### 作業内容
- `terraform/iam.tf` に以下を定義する：
  1. `aws_iam_role` (Lambda 実行ロール)：
     - `name`: `"${var.project_name}-lambda-role"`
     - `assume_role_policy`: Lambda サービスへの信頼ポリシー
  2. `aws_iam_role_policy` (インラインポリシー)：
     - DynamoDB `PutItem` 権限（対象テーブルのみ）
     - CloudWatch Logs `CreateLogGroup`、`CreateLogStream`、`PutLogEvents` 権限（対象ロググループのみ）
     - **最小権限**: `*` リソース指定は使用しないこと

#### 作成・変更対象
- `grafana-demo-alerts/terraform/iam.tf`

#### 前提条件
- TASK-007 完了

#### 完了条件
- `terraform validate` が成功すること
- ポリシーが DynamoDB と CloudWatch Logs の最小権限のみであること

#### 確認方法
- `terraform plan` で IAM ロールとポリシーが計画されること

#### 依存タスク
- TASK-007

#### 注意点
- DynamoDB の権限対象リソースは `aws_dynamodb_table.main.arn` に限定する
- CloudWatch Logs の権限対象は `/aws/lambda/${local.lambda_name}:*` に限定する
- `GetItem` は今回必須ではないが、重複 alertId チェックを実装する場合は追加する

---

### TASK-015: `cloudwatch.tf` - Lambda ロググループ定義

#### 区分
- 必須（US1）

#### 目的
- Lambda のロググループを明示的に Terraform で管理し、保持期間を設定する

#### 作業内容
- `terraform/cloudwatch.tf` に `aws_cloudwatch_log_group` リソースを定義する：
  - `name`: `local.log_group_name`（= `/aws/lambda/grafana-demo-alert-handler`）
  - `retention_in_days`: `var.log_retention_days`（= 3）

#### 作成・変更対象
- `grafana-demo-alerts/terraform/cloudwatch.tf`

#### 前提条件
- TASK-007 完了

#### 完了条件
- `terraform validate` が成功すること

#### 確認方法
- `terraform plan` でロググループが計画されること

#### 依存タスク
- TASK-007

#### 注意点
- Lambda 関数を先に作成すると Lambda が自動でロググループを作成してしまうため、Terraform で先に定義する
- 保持期間 3 日はコスト抑制のための設定（本番では適切な値に変更する）

---

### TASK-016: `lambda.tf` - Lambda 関数定義

#### 区分
- 必須（US1）

#### 目的
- Lambda 関数を Terraform で定義し、`handler.py` をデプロイ可能な状態にする

#### 作業内容
- `terraform/lambda.tf` に以下を定義する：
  1. `data "archive_file" "lambda_zip"`:
     - `type = "zip"`
     - `source_file = "../lambda/handler.py"`
     - `output_path = "../lambda/handler.zip"`
  2. `aws_lambda_function "main"`:
     - `function_name = local.lambda_name`
     - `runtime = "python3.12"`
     - `handler = "handler.lambda_handler"`
     - `filename = data.archive_file.lambda_zip.output_path`
     - `source_code_hash = data.archive_file.lambda_zip.output_base64sha256`
     - `role = aws_iam_role.lambda.arn`
     - `memory_size = var.lambda_memory_size`（128 MB）
     - `timeout = var.lambda_timeout`（10 秒）
     - `environment.variables`: `TABLE_NAME = local.table_name`、`LOG_LEVEL = "INFO"`
     - `depends_on = [aws_cloudwatch_log_group.lambda]`

#### 作成・変更対象
- `grafana-demo-alerts/terraform/lambda.tf`

#### 前提条件
- TASK-010〜TASK-012 完了（`handler.py` 存在）
- TASK-014 完了（IAM ロール参照のため）
- TASK-015 完了（ロググループ参照のため）

#### 完了条件
- `terraform validate` が成功すること
- `terraform plan` で Lambda 関数作成が計画されること

#### 確認方法
- `terraform plan | grep aws_lambda_function` で計画確認

#### 依存タスク
- TASK-010〜TASK-012、TASK-014、TASK-015

#### 注意点
- `source_code_hash` を設定することで handler.py の変更時に Lambda が自動更新される
- `depends_on` でロググループの先行作成を保証する（自動作成競合防止）
- `handler.zip` は `.gitignore` に含めること

---

### TASK-017: `apigateway.tf` - API Gateway HTTP API 定義

#### 区分
- 必須（US1）

#### 目的
- API Gateway HTTP API、route、integration、stage、Lambda permission を定義し、curl から Lambda を呼び出せるようにする

#### 作業内容
- `terraform/apigateway.tf` に以下を定義する：
  1. `aws_apigatewayv2_api "main"`:
     - `name = "${var.project_name}-api"`
     - `protocol_type = "HTTP"`
     - CORS: 不要（curl からのリクエストのみのため）
  2. `aws_apigatewayv2_stage "default"`:
     - `api_id = aws_apigatewayv2_api.main.id`
     - `name = "$default"`, `auto_deploy = true`
  3. `aws_apigatewayv2_integration "lambda"`:
     - `integration_type = "AWS_PROXY"`
     - `integration_uri = aws_lambda_function.main.invoke_arn`
     - `payload_format_version = "2.0"`
  4. `aws_apigatewayv2_route "post_alerts"`:
     - `route_key = "POST /alerts"`
     - `target = "integrations/${aws_apigatewayv2_integration.lambda.id}"`
  5. `aws_lambda_permission "apigw"`:
     - `action = "lambda:InvokeFunction"`
     - `principal = "apigateway.amazonaws.com"`
     - `source_arn = "${aws_apigatewayv2_api.main.execution_arn}/*/*"`

#### 作成・変更対象
- `grafana-demo-alerts/terraform/apigateway.tf`

#### 前提条件
- TASK-016 完了（Lambda 関数参照のため）

#### 完了条件
- `terraform validate` が成功すること
- `terraform apply` 後に API エンドポイント URL が `outputs.tf` に出力されること

#### 確認方法
- `terraform output api_endpoint` で URL が出力されること

#### 依存タスク
- TASK-016

#### 注意点
- `payload_format_version = "2.0"` を設定すること（HTTP API の Lambda 統合に対応するため）
- `auto_deploy = true` でデプロイを自動化する
- `source_arn` の末尾は `/*/*` とし、全メソッド・パスへのアクセスを許可する

---

### TASK-018: `grafana.tf` - Managed Grafana Workspace 定義

#### 区分
- 必須（US2）

#### 目的
- Amazon Managed Grafana のワークスペースを Terraform で作成する

#### 作業内容
- `terraform/grafana.tf` に以下を定義する：
  1. `aws_grafana_workspace "main"`:
     - `name = "${var.project_name}-workspace"`
     - `account_access_type = "CURRENT_ACCOUNT"`
     - `authentication_providers = ["AWS_SSO"]`  
       ※ Managed Grafana は `AWS_SSO` または `SAML` が必要。組み込み認証は `AWS_SSO` 経由で設定する
     - `permission_type = "SERVICE_MANAGED"`
     - `role_arn = aws_iam_role.grafana.arn`
     - `data_sources = ["CLOUDWATCH"]`

#### 作成・変更対象
- `grafana-demo-alerts/terraform/grafana.tf`

#### 前提条件
- TASK-019 完了（Grafana IAM ロール参照のため）

#### 完了条件
- `terraform apply` 後に Grafana Workspace が作成されること
- `terraform output grafana_endpoint` で URL が出力されること

#### 確認方法
- AWS コンソール → Amazon Managed Grafana でワークスペースを確認

#### 依存タスク
- TASK-019

#### 注意点
- Managed Grafana は `AWS_SSO` を認証方式として指定する必要がある
- `data_sources = ["CLOUDWATCH"]` を指定することで Grafana が CloudWatch に自動接続できる権限設定が有効になる
- Workspace 作成には数分かかる場合がある

---

### TASK-019: `iam.tf` 追記 - Grafana 用 IAM ロール・ポリシー定義

#### 区分
- 必須（US2）

#### 目的
- Grafana が CloudWatch メトリクス・ログを参照するための IAM ロールを定義する

#### 作業内容
- `terraform/iam.tf` に以下を追記する：
  1. `aws_iam_role` (Grafana ロール)：
     - `name = "${var.project_name}-grafana-role"`
     - `assume_role_policy`: Grafana サービスへの信頼ポリシー（`grafana.amazonaws.com`）
  2. `aws_iam_role_policy_attachment` または `aws_iam_role_policy`：
     - AWS 管理ポリシー `CloudWatchReadOnlyAccess` をアタッチ
     - `CloudWatchLogsReadOnlyAccess` をアタッチ
     - ※ 今回使用しない X-Ray / Prometheus / Timestream 等の権限は付与しない

#### 作成・変更対象
- `grafana-demo-alerts/terraform/iam.tf`（TASK-014 に追記）

#### 前提条件
- TASK-014 完了

#### 完了条件
- `terraform validate` が成功すること
- IAM ロールに CloudWatch 参照権限のみが付与されていること

#### 確認方法
- `terraform plan` で Grafana IAM ロール・ポリシーが計画されること

#### 依存タスク
- TASK-014

#### 注意点
- `CloudWatchReadOnlyAccess` は AWS 管理ポリシーで CloudWatch メトリクスの参照権限を含む
- X-Ray / Prometheus / Timestream は今回未使用のため付与しないこと

---

## 10. Phase 5: Terraform 実行

---

### TASK-020: `terraform init` / `fmt` / `validate` / `plan` 実行

#### 区分
- 必須

#### 目的
- Terraform コードの品質を確認し、適用前に実行計画を検証する

#### 作業内容
- 以下のコマンドを順番に実行する：

```bash
cd grafana-demo-alerts/terraform

# 1. フォーマット確認・修正
terraform fmt

# 2. 構文・スキーマ検証
terraform validate

# 3. 初期化（プロバイダーのダウンロード）
terraform init

# 4. 実行計画確認
terraform plan
```

- `terraform plan` の出力で以下を確認する：
  - 作成リソース数が想定と一致すること
  - 意図しない削除・変更がないこと
  - エラーがないこと

#### 作成・変更対象
- なし（確認のみ。Terraform ファイルに修正が必要な場合は修正する）

#### 前提条件
- TASK-013〜TASK-019 完了（全 `.tf` ファイル定義済み）
- `handler.py` が存在すること（TASK-012 完了）

#### 完了条件
- `terraform fmt` でエラーなし
- `terraform validate` で `Success!` と表示されること
- `terraform plan` でリソース作成が計画されること（エラーなし）

#### 確認方法
- 各コマンドの終了コードが 0 であること

#### 依存タスク
- TASK-013〜TASK-019

#### 注意点
- `terraform plan` 出力の `Plan: X to add, 0 to change, 0 to destroy` を確認すること
- 想定外のリソース削除がある場合は原因を調査すること（前回の apply 残存等）

---

### TASK-021: `terraform apply` 実行・リソース確認

#### 区分
- 必須

#### 目的
- AWS 上に全リソースを作成し、実際に稼働する状態にする

#### 作業内容
- `terraform apply` を実行する：

```bash
cd grafana-demo-alerts/terraform
terraform apply
# 確認プロンプトで "yes" と入力
```

- 適用完了後、以下の出力値を確認・メモする：

```bash
terraform output
```

| 出力値 | 確認内容 |
|---|---|
| `api_endpoint` | URL 形式であること |
| `lambda_function_name` | `grafana-demo-alert-handler` であること |
| `dynamodb_table_name` | `grafana-demo-alerts` であること |
| `log_group_name` | `/aws/lambda/grafana-demo-alert-handler` であること |
| `grafana_workspace_id` | ID が出力されること |
| `grafana_endpoint` | URL 形式であること |

#### 作成・変更対象
- AWS リソース（DynamoDB / Lambda / API Gateway / CloudWatch Logs / Managed Grafana / IAM）

#### 前提条件
- TASK-020 完了（`terraform plan` でエラーなし）

#### 完了条件
- `terraform apply` が成功すること（終了コード 0）
- 全 output 値が表示されること

#### 確認方法
- AWS コンソールで各リソースの存在を確認する

#### 依存タスク
- TASK-020

#### 注意点
- 適用完了後すぐに課金が開始される（特に Managed Grafana は月額固定）
- 作業を中断する場合は `terraform destroy` でリソースを削除すること
- API エンドポイント URL をメモしておくこと（後続タスクで使用）

---

## 11. Phase 6: API 動作確認（US1）

---

### TASK-022: 正常系リクエスト送信

#### 区分
- 必須（US1）

#### 目的
- API が正常に動作し、疑似アラートを受け付けることを確認する

#### 作業内容
- `terraform output -raw api_endpoint` で API エンドポイント URL を取得する
- 以下の 3 種類のサンプルデータを curl で送信する：

```bash
# エンドポイント取得
API_ENDPOINT=$(cd terraform && terraform output -raw api_endpoint)

# critical 送信
curl -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d @samples/alert-critical.json \
  -w "\nHTTP Status: %{http_code}\n"

# warning 送信
curl -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d @samples/alert-warning.json \
  -w "\nHTTP Status: %{http_code}\n"

# info 送信
curl -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d @samples/alert-info.json \
  -w "\nHTTP Status: %{http_code}\n"
```

#### 作成・変更対象
- なし（確認のみ）

#### 前提条件
- TASK-021 完了（API Gateway / Lambda / DynamoDB が作成済み）

#### 完了条件
- 3 件ともに HTTP 200 が返ること
- レスポンスボディに `"stored": true` が含まれること

#### 確認方法
- HTTP Status が 200 であること
- レスポンスボディ: `{"message": "alert accepted", "alertId": "...", "stored": true}`

#### 依存タスク
- TASK-021

#### 注意点
- `Content-Type: application/json` ヘッダーを必ず付けること
- エンドポイント URL には `/alerts` パスが含まれていること

---

### TASK-023: 異常系リクエスト送信・エラーケース確認

#### 区分
- 必須（US1）

#### 目的
- バリデーションエラーが正しく HTTP 400 で返ることを確認する

#### 作業内容
- 以下の異常系ケースを curl で送信し、期待するエラーレスポンスを確認する：

```bash
API_ENDPOINT=$(cd terraform && terraform output -raw api_endpoint)

# ケース1: severity 不正
curl -s -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{"alertId":"ERR-001","facilityId":"FAC-001","facilityName":"設備","severity":"high","alertType":"test","message":"test","occurredAt":"2026-04-25T10:00:00+09:00"}' \
  -w "\nStatus: %{http_code}"

# ケース2: 必須フィールド欠損（severityなし）
curl -s -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{"alertId":"ERR-002","facilityId":"FAC-001"}' \
  -w "\nStatus: %{http_code}"

# ケース3: occurredAt形式不正
curl -s -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{"alertId":"ERR-003","facilityId":"FAC-001","facilityName":"設備","severity":"info","alertType":"test","message":"test","occurredAt":"2026/04/25"}' \
  -w "\nStatus: %{http_code}"

# ケース4: 空リクエスト
curl -s -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{}' \
  -w "\nStatus: %{http_code}"
```

#### 作成・変更対象
- なし（確認のみ）

#### 前提条件
- TASK-022 完了（正常系が動作確認済み）

#### 完了条件
- 全ケースで HTTP 400 が返ること
- レスポンスボディに `"error"` フィールドが含まれること

#### 確認方法
- HTTP ステータスコードが 400 であること
- エラーコードが期待値と一致すること（例: `INVALID_SEVERITY`、`MISSING_FIELD` 等）

#### 依存タスク
- TASK-022

#### 注意点
- HTTP 400 の代わりに 500 が返る場合は handler.py の例外処理を確認すること

---

### TASK-024: DynamoDB コンソールでのデータ保存確認

#### 区分
- 必須（US1）

#### 目的
- TASK-022 で送信したデータが DynamoDB に正しく保存されていることを確認する

#### 作業内容
- AWS コンソール → DynamoDB → テーブル → `grafana-demo-alerts` を開く
- 「テーブルアイテムの探索」で以下を確認する：
  - `ALT-0001`（critical）、`ALT-0002`（warning）、`ALT-0003`（info）の 3 件が存在すること
  - 各レコードに `receivedAt`、`source`、`status` が付与されていること
  - `receivedAt` が UTC 形式（`Z` で終わる）であること
  - `source = "api"`、`status = "open"` であること

#### 作成・変更対象
- なし（確認のみ）

#### 前提条件
- TASK-022 完了

#### 完了条件
- 3 件のレコードが DynamoDB テーブルに存在すること

#### 確認方法
- AWS コンソールのデータ一覧で目視確認

#### 依存タスク
- TASK-022

#### 注意点
- `occurredAt` は送信した値（`+09:00` 形式）がそのまま保存されていること
- `receivedAt` は UTC 形式（`2026-04-25T...Z`）であること

---

## 12. Phase 7: CloudWatch 確認（US1）

---

### TASK-025: CloudWatch Logs で Lambda 処理ログ確認

#### 区分
- 必須（US1）

#### 目的
- Lambda が JSON 構造化ログを CloudWatch Logs に正しく出力していることを確認する

#### 作業内容
- AWS コンソール → CloudWatch → ロググループ → `/aws/lambda/grafana-demo-alert-handler`
- 最新のログストリームを開き、以下のログイベントを確認する：
  - `"event": "REQUEST_RECEIVED"` が出力されていること
  - `"event": "STORED"` が出力されていること
  - ログが JSON 形式であること（`{` で始まること）

#### 作成・変更対象
- なし（確認のみ）

#### 前提条件
- TASK-022〜TASK-023 完了（Lambda が実行済み）

#### 完了条件
- JSON 形式のログが出力されていること
- 正常ログ・エラーログが期待するイベント種別で記録されていること

#### 確認方法
- AWS コンソールのロググループ画面で目視確認

#### 依存タスク
- TASK-022、TASK-023

#### 注意点
- ログが表示されない場合は Lambda 実行ロールの権限を確認すること（TASK-014）

---

### TASK-026: CloudWatch Metrics で各サービスメトリクス確認

#### 区分
- 必須（US1）

#### 目的
- API Gateway / Lambda / DynamoDB の標準メトリクスが CloudWatch に蓄積されていることを確認する

#### 作業内容
- AWS コンソール → CloudWatch → メトリクス → すべてのメトリクス
- 以下の名前空間・メトリクスを確認する：

| 名前空間 | メトリクス | 確認内容 |
|---|---|---|
| `AWS/ApiGateway` | `Count` | リクエスト数が増加していること |
| `AWS/ApiGateway` | `4XXError` / `5XXError` | エラー件数が確認できること |
| `AWS/Lambda` | `Invocations` | 実行回数が増加していること |
| `AWS/Lambda` | `Errors` | エラー件数が確認できること |
| `AWS/DynamoDB` | `ConsumedWriteCapacityUnits` | 書き込みが記録されていること |

#### 作成・変更対象
- なし（確認のみ）

#### 前提条件
- TASK-022〜TASK-023 完了（リクエスト送信済み）

#### 完了条件
- 上記 5 つのメトリクスが CloudWatch コンソールで確認できること

#### 確認方法
- AWS コンソールのメトリクス画面で目視確認

#### 依存タスク
- TASK-022、TASK-023

#### 注意点
- メトリクスの反映には最大 5 分程度かかる場合がある

---

### TASK-027: Logs Insights クエリ動作確認

#### 区分
- 必須（US1）

#### 目的
- CloudWatch Logs Insights クエリが正常に動作し、severity 別集計が可能であることを確認する

#### 作業内容
- AWS コンソール → CloudWatch → ログ → ログのインサイト
- ロググループ `/aws/lambda/grafana-demo-alert-handler` を選択
- 以下の 3 クエリを実行し、結果を確認する：

**クエリ 1: Lambda エラー確認**
```sql
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 20
```

**クエリ 2: severity 別件数**

CloudWatch Logs Insights は JSON ログのフィールドを自動展開するため、`severity` / `event` フィールドへ直接アクセスできる。

```sql
fields @timestamp, severity, event
| filter event = "REQUEST_RECEIVED"
| stats count() by severity
```

**クエリ 3: アラート件数推移（5 分ごと）**

handler.py が出力するイベント名 `STORED`（DynamoDB 保存成功時）を集計対象とする。

```sql
fields @timestamp, event
| filter event = "STORED"
| stats count() by bin(5m)
```

- クエリ結果をスクリーンショットまたはメモとして保存する（任意）

#### 作成・変更対象
- なし（確認のみ）

#### 前提条件
- TASK-022〜TASK-023 完了（ログが出力済み）

#### 完了条件
- クエリ 2 で severity 別の件数（critical: 1、warning: 1、info: 1）が表示されること

#### 確認方法
- Logs Insights クエリの結果画面で目視確認

#### 依存タスク
- TASK-025（JSON ログが出力済みであること）

#### 注意点
- ログが JSON 形式でない場合はクエリ結果が期待通りにならない場合がある
- JSON 形式ログの場合は以下のクエリでより正確に集計できる：

```sql
fields @timestamp, severity
| filter event = "REQUEST_RECEIVED"
| stats count() by severity
```

---

## 13. Phase 8: Amazon Managed Grafana 設定（US2）

---

### TASK-028: Grafana 初回ログイン・Admin ユーザー設定

#### 区分
- 必須（US2）

#### 目的
- Grafana ワークスペースに初回ログインし、利用開始できる状態にする

#### 作業内容
1. `terraform output grafana_endpoint` で Grafana URL を確認する
2. AWS コンソール → Amazon Managed Grafana → ワークスペース → `grafana-demo-workspace`
3. 「ワークスペース URL」をクリックして Grafana 画面を開く
4. 初回ログインを完了する（AWS SSO 経由 / 組み込み認証）
5. Admin ユーザーとしてログインできることを確認する

#### 作成・変更対象
- なし（手動設定）

#### 前提条件
- TASK-021 完了（Grafana Workspace が作成済み）

#### 完了条件
- Grafana のホーム画面にアクセスできること

#### 確認方法
- ブラウザで Grafana URL を開き、ダッシュボード画面が表示されること

#### 依存タスク
- TASK-021

#### 注意点
- Managed Grafana の初回ログインは AWS アカウントのサインインと連動する
- ログイン後は Admin 権限でユーザーが設定されていることを確認する
- 設定手順は `docs/dashboard.md` に記録すること（任意）

---

### TASK-029: CloudWatch Data Source 設定・接続確認

#### 区分
- 必須（US2）

#### 目的
- Grafana から CloudWatch メトリクス・ログを参照できるようにする

#### 作業内容
1. Grafana 左メニュー → Connections → Data sources → 「Add data source」
2. 「CloudWatch」を選択
3. 以下を設定する：
   - **Authentication Provider**: `AWS SDK Default`（Grafana IAM ロールを自動使用）
   - **Default Region**: `ap-northeast-1`
4. 「Save & test」をクリック
5. 「Data source is working」または「CloudWatch data source is working」と表示されることを確認する

#### 作成・変更対象
- Grafana CloudWatch データソース設定（手動設定）

#### 前提条件
- TASK-028 完了（Grafana ログイン済み）
- TASK-019 完了（Grafana IAM ロールが作成済み）

#### 完了条件
- 「Save & test」が成功し、接続確認メッセージが表示されること

#### 確認方法
- Grafana Data Sources 画面で CloudWatch が「Connected」状態であること

#### 依存タスク
- TASK-028、TASK-019

#### 注意点
- 接続失敗の場合は Grafana IAM ロールの権限を確認すること（TASK-019）
- `AWS SDK Default` を選択することで Grafana ワークスペースに紐付いた IAM ロールが自動使用される

---

## 14. Phase 9: Grafana ダッシュボード作成（US2）

---

### TASK-030: 必須パネル作成（API Gateway / Lambda / DynamoDB メトリクス）

#### 区分
- 必須（US2）

#### 目的
- AWS 各サービスの主要メトリクスを可視化するパネルをダッシュボードに追加する

#### 作業内容
1. Grafana 左メニュー → Dashboards → 「New dashboard」→「Add visualization」
2. Data source: **CloudWatch** を選択
3. 以下の 6 パネルを作成する：

| パネル名 | Namespace | MetricName | 統計 | ビジュアル |
|---|---|---|---|---|
| API リクエスト数 | AWS/ApiGateway | Count | Sum | Time series |
| API エラー数（4xx/5xx） | AWS/ApiGateway | 4xx + 5xx（HTTP API は小文字） | Sum | Time series |
| Lambda 実行回数 | AWS/Lambda | Invocations | Sum | Stat |
| Lambda エラー数 | AWS/Lambda | Errors | Sum | Stat |
| Lambda 実行時間 | AWS/Lambda | Duration | Average | Time series |
| DynamoDB 書き込み | AWS/DynamoDB | ConsumedWriteCapacityUnits | Sum | Time series |

4. ダッシュボード名を `Pseudo Facility Alert Monitoring` に設定する
5. 「Save dashboard」で保存する

#### 作成・変更対象
- Grafana ダッシュボード（手動作成）

#### 前提条件
- TASK-029 完了（CloudWatch Data Source 接続済み）

#### 完了条件
- 6 パネルが作成され、データが表示されていること（または数分後に表示されること）

#### 確認方法
- 各パネルにグラフまたは値が表示されること（TASK-022 で送信したリクエスト分）

#### 依存タスク
- TASK-022（データが存在すること）、TASK-029

#### 注意点
- Grafana の時間範囲を「過去 1 時間」に設定すること
- メトリクスが表示されない場合は時間範囲・リージョン・ディメンションを確認すること
- API Gateway のディメンションは `ApiName` で絞り込むこと

---

### TASK-031: アラート件数パネル作成（Logs Insights）

#### 区分
- 必須（US2）

#### 目的
- 疑似アラートの件数・severity 別内訳を可視化するパネルを追加する

#### 作業内容
1. TASK-030 で作成したダッシュボードを編集する
2. 以下の 2 パネルを追加する（Data source: CloudWatch）：

**パネル 1: アラート総件数**
- クエリタイプ: `CloudWatch Logs Insights`
- ロググループ: `/aws/lambda/grafana-demo-alert-handler`

```sql
fields @timestamp, @message
| filter event = "STORED"
| stats count() as total_alerts
```
- ビジュアル: Stat

**パネル 2: severity 別アラート件数**
- クエリタイプ: `CloudWatch Logs Insights`
- ロググループ: `/aws/lambda/grafana-demo-alert-handler`

```sql
fields @timestamp, severity
| filter event = "REQUEST_RECEIVED"
| stats count() by severity
```
- ビジュアル: Bar chart または Table

3. ダッシュボードを保存する

#### 作成・変更対象
- Grafana ダッシュボード（手動編集）

#### 前提条件
- TASK-030 完了
- TASK-027 完了（Logs Insights クエリが動作確認済み）

#### 完了条件
- アラート総件数パネルに件数が表示されること（3 件）
- severity 別パネルに critical / warning / info の内訳が表示されること

#### 確認方法
- 各パネルの表示値が TASK-022 で送信したデータと一致すること

#### 依存タスク
- TASK-030

#### 注意点
- Logs Insights クエリは標準メトリクスと異なり、クエリ実行コストが発生する（少量なら無視できる）
- ログが JSON 構造化形式でない場合はクエリを調整すること（TASK-027 参照）

---

### TASK-032: ダッシュボード JSON エクスポート・`docs/dashboard.md` 作成

#### 区分
- 必須（US2）

#### 目的
- 作成したダッシュボードを JSON としてエクスポートし、再現・再利用できる状態で保存する

#### 作業内容
1. Grafana ダッシュボード画面右上の「Share」アイコンをクリック
2. 「Export」タブ → 「Export for sharing externally」を ON にする
3. 「Save to file」でダウンロードし、`docs/dashboard-export.json` として保存する
4. `docs/dashboard.md` を作成し、以下を記載する：
   - ダッシュボード作成手順の概要
   - 各パネルの設定内容（メトリクス・クエリ）
   - JSON エクスポートからの復元手順
   - Grafana Alerting 設定手順（任意拡張向けメモ）

#### 作成・変更対象
- `grafana-demo-alerts/docs/dashboard-export.json`
- `grafana-demo-alerts/docs/dashboard.md`

#### 前提条件
- TASK-031 完了（ダッシュボード作成済み）

#### 完了条件
- `dashboard-export.json` が存在し、有効な JSON であること
- `dashboard.md` に手順が記載されていること

#### 確認方法
- `cat docs/dashboard-export.json | python3 -m json.tool` で JSON バリデーション

#### 依存タスク
- TASK-031

#### 注意点
- 「Export for sharing externally」を ON にすることで、データソース名ではなく変数参照に変換される
- JSON ファイルは Git にコミットして再利用できるようにすること

---

## 15. Phase 10: テスト

---

### TASK-033: 正常系・異常系・可視化の統合テスト

#### 区分
- 必須

#### 目的
- システム全体が受け入れ条件を満たすことを確認する

#### 作業内容
- 以下のチェックリストを順番に確認する：

**正常系テスト**
- [ ] critical / warning / info の各アラートを POST → HTTP 200 が返ること
- [ ] DynamoDB に 3 件のレコードが保存されていること
- [ ] CloudWatch Logs に JSON ログが出力されていること
- [ ] Grafana で API リクエスト数が増加していること

**異常系テスト**
- [ ] severity 不正 → HTTP 400 + `{"error": "INVALID_SEVERITY", ...}` が返ること
- [ ] 必須フィールド欠損 → HTTP 400 + `{"error": "MISSING_FIELD", ...}` が返ること
- [ ] occurredAt 形式不正 → HTTP 400 + `{"error": "INVALID_DATE_FORMAT", ...}` が返ること
- [ ] 空リクエスト → HTTP 400 + `{"error": "EMPTY_BODY", ...}` が返ること

**可視化確認テスト**
- [ ] Grafana ダッシュボードで API リクエスト数パネルにデータが表示されること
- [ ] Lambda 実行回数パネルにデータが表示されること
- [ ] Lambda エラー数パネルにデータが表示されること（異常系テスト後）
- [ ] アラート総件数パネルに 3 件と表示されること
- [ ] severity 別パネルに critical / warning / info の内訳が表示されること

**Terraform テスト**
- [ ] `terraform fmt` が成功すること
- [ ] `terraform validate` が成功すること
- [ ] `terraform plan` で変更なし（`0 to add, 0 to change, 0 to destroy`）と表示されること

#### 作成・変更対象
- なし（確認のみ）

#### 前提条件
- Phase 1〜9 の必須タスクすべて完了

#### 完了条件
- 上記チェックリストが全て ✅ であること

#### 確認方法
- 各チェック項目の目視確認

#### 依存タスク
- Phase 1〜9 の全必須タスク

#### 注意点
- Grafana メトリクスの反映には数分かかる場合がある
- 異常系テスト後の Lambda エラーは Grafana の Errors パネルに反映されること

---

### TASK-034: README 最終版更新

#### 区分
- 必須

#### 目的
- 構築・確認・削除手順が整理された最終版 README を完成させる

#### 作業内容
- `README.md` を最終版に更新する：
  - 作成された AWS リソース一覧（実際のリソース名・ARN は記載しない）
  - 構築手順（terraform apply）
  - API 動作確認手順（curl コマンド例）
  - Grafana 設定手順の概要（詳細は `docs/dashboard.md` へのリンク）
  - 削除手順（terraform destroy）
  - Terraform 管理外の手動設定一覧（Grafana Data Source / Dashboard）

#### 作成・変更対象
- `grafana-demo-alerts/README.md`

#### 前提条件
- TASK-033 完了

#### 完了条件
- README に構築・確認・削除の各手順が記載されていること
- 手動設定が必要な箇所が明示されていること

#### 確認方法
- README を通読し、初見の人が手順に従って構築できることを確認する

#### 依存タスク
- TASK-033

#### 注意点
- 機密情報（AWS アカウント ID・エンドポイント URL・ARN）を README に記載しないこと

---

## 16. Phase 11: 削除作業（US4）

---

### TASK-035: `terraform destroy` 実行

#### 区分
- 必須（US4）

#### 目的
- 検証後の AWS リソースを確実に削除し、継続課金を防止する

#### 作業内容
```bash
cd grafana-demo-alerts/terraform

# 削除前に対象リソースを確認
terraform plan -destroy

# 削除実行
terraform destroy
# 確認プロンプトで "yes" と入力
```

- `Destroy complete! Resources: X destroyed.` と表示されることを確認する

#### 作成・変更対象
- AWS リソースの削除（DynamoDB / Lambda / API Gateway / CloudWatch Logs / Managed Grafana / IAM）

#### 前提条件
- TASK-033 完了（テスト完了後）

#### 完了条件
- `terraform destroy` が成功すること（終了コード 0）

#### 確認方法
- `terraform state list` が空（または state ファイルなし）になること

#### 依存タスク
- TASK-033

#### 注意点
- **Managed Grafana Workspace の削除には時間がかかる場合がある**
- Terraform 管理外でダッシュボード等を手動作成した場合は Grafana 内のデータも削除されることに注意
- 削除失敗した場合は AWS コンソールで手動削除する（TASK-036）

---

### TASK-036: AWS コンソールでの削除漏れ確認

#### 区分
- 必須（US4）

#### 目的
- `terraform destroy` で削除できなかったリソースがないことを確認し、課金が停止することを確認する

#### 作業内容
- AWS コンソールで以下のリソースが存在しないことを確認する：

| 確認場所 | 確認内容 |
|---|---|
| API Gateway → HTTP APIs | `grafana-demo-*` が存在しないこと |
| Lambda → Functions | `grafana-demo-*` が存在しないこと |
| DynamoDB → Tables | `grafana-demo-alerts` が存在しないこと |
| CloudWatch → Log groups | `/aws/lambda/grafana-demo-*` が存在しないこと |
| Amazon Managed Grafana | ワークスペースが存在しないこと |
| IAM → Roles | `grafana-demo-*` が存在しないこと |

- 手動設定した Grafana ダッシュボード・Data Source は Workspace 削除と同時に削除されることを確認する

#### 作成・変更対象
- なし（確認・手動削除）

#### 前提条件
- TASK-035 完了

#### 完了条件
- 上記リソースが全て削除されていること

#### 確認方法
- AWS コンソールの各サービス画面での目視確認

#### 依存タスク
- TASK-035

#### 注意点
- IAM ロールが残存している場合は手動で削除すること
- `terraform destroy` 失敗時は AWS コンソールから手動削除する
- `docs/cleanup.md` を作成し、削除確認チェックリストを記録することを推奨する（任意）

---

### TASK-037: ローカルの state ファイル・一時ファイル整理

#### 区分
- 必須（US4）

#### 目的
- Terraform state ファイル等の機密情報を含む可能性のあるファイルを削除する

#### 作業内容
```bash
cd grafana-demo-alerts

# Terraform state ファイル削除
rm -f terraform/terraform.tfstate
rm -f terraform/terraform.tfstate.backup

# Lambda ZIP パッケージ削除
rm -f lambda/handler.zip

# Terraform プロバイダーキャッシュ削除（任意）
rm -rf terraform/.terraform/
rm -f terraform/.terraform.lock.hcl
```

#### 作成・変更対象
- ローカルファイルの削除

#### 前提条件
- TASK-036 完了（全リソース削除確認済み）

#### 完了条件
- `terraform.tfstate` が存在しないこと

#### 確認方法
- `ls terraform/` で state ファイルが存在しないことを確認

#### 依存タスク
- TASK-036

#### 注意点
- state ファイルには AWS アカウント ID・ARN 等が含まれるため、適切に削除すること
- `.gitignore` に `*.tfstate` が含まれていることで Git コミット時の混入は防げているが、ローカル削除も推奨

---

## 17. 完了条件

以下がすべて達成されたことをもって本タスク書の作業完了とする：

| # | 受け入れ条件 | 確認タスク |
|---|---|---|
| AC-001 | Terraform で AWS リソースを作成できる | TASK-021 |
| AC-002 | API Gateway に正常な疑似アラートを POST できる | TASK-022 |
| AC-003 | Lambda が正常に処理する | TASK-022、TASK-025 |
| AC-004 | DynamoDB にアラートデータが保存される | TASK-024 |
| AC-005 | CloudWatch Logs で処理ログを確認できる | TASK-025 |
| AC-006 | CloudWatch Metrics で主要メトリクスを確認できる | TASK-026 |
| AC-007 | Amazon Managed Grafana から CloudWatch をデータソースとして参照できる | TASK-029 |
| AC-008 | Grafana ダッシュボードで最低限のメトリクスを確認できる | TASK-030、TASK-031 |
| AC-009 | 異常系リクエストに対して適切なエラーレスポンスを返せる | TASK-023 |
| AC-010 | `terraform destroy` で Terraform 管理対象リソースを削除できる | TASK-035 |
| AC-011 | 削除漏れ確認ができる | TASK-036 |
| AC-012 | README に構築・確認・削除手順が整理されている | TASK-034 |

---

## 18. 注意事項

### コスト管理
- `terraform apply` 後は課金が開始する（特に Amazon Managed Grafana は月額約 9 USD 固定）
- 検証完了後は必ず `terraform destroy` を実行すること
- 作業を中断する場合は一時的でも `terraform destroy` を実行することを推奨する

### セキュリティ
- API エンドポイント URL が公開されるため、長期稼働させないこと
- `terraform.tfstate` を Git にコミットしないこと（`.gitignore` 確認）
- 実データ・機密情報・個人情報を送信しないこと

### 実装ガイドライン
- 最小構成で動作確認を優先し、過剰な作り込みはしない
- IAM 権限は最小権限を意識し、`*` リソース指定を使用しない
- リソース名は `grafana-demo-` プレフィックスで統一する

---

## 19. 任意拡張タスク

以下は今回の必須スコープには含まれないが、時間があれば対応可能：

### OPT-001: Grafana Alerting 設定（US3）

**目的**: Lambda エラー数 > 0 の場合に Grafana でアラート状態になることを確認する

**作業内容**:
- Grafana → Alerting → Alert rules → 「New alert rule」
- Lambda Errors メトリクスが閾値超過時に Firing になるルールを 1 件設定する
- 通知先設定は不要（UI での Firing 確認のみ）

**完了条件**: 異常系リクエスト送信後に Grafana Alerting 画面でルールが Firing 状態になること

---

### OPT-002: Grafana ダッシュボード追加パネル

**目的**: レイテンシ・DynamoDB スロットル等の追加パネルを作成する

**作業内容**: TASK-030 のダッシュボードに以下を追加
- API Gateway Latency パネル
- DynamoDB ThrottledRequests パネル

---

### OPT-003: `docs/cleanup.md` 作成

**目的**: 削除確認チェックリストをドキュメント化する

**作業内容**: TASK-036 の確認内容を `docs/cleanup.md` としてドキュメント化

---

## 20. Claude Code 向け実装時の注意事項

以下は本システムの実装を Claude Code に依頼する際の共通指示である：

### 実装方針

1. **最小構成優先**: 動作確認に必要な最低限の実装のみ行う。過剰な抽象化・設計パターン適用・エラーハンドリングの作り込みは不要
2. **Terraform 管理**: AWS リソースは原則 Terraform で定義する。コンソールでの手動リソース作成は避ける
3. **local backend**: Terraform の state は local backend（デフォルト）のみ。S3 remote backend は使用しない
4. **module 分割不要**: Terraform モジュール分割は行わない。全リソースをフラットに定義する
5. **命名統一**: 全リソース名に `grafana-demo-` プレフィックスを使用する
6. **コスト抑制**: カスタムメトリクスを作成しない。高頻度ポーリングを実装しない
7. **JSON ログ**: Lambda のログ出力は `print(json.dumps({...}))` 形式の JSON 構造化ログを使用する

### 実装順序

必ず以下の順序で実装し、各フェーズで動作確認を行う：

```
Phase 3 (Lambda) → Phase 4 (Terraform定義) → Phase 5 (apply) → Phase 6〜7 (US1確認) → Phase 8〜9 (US2確認)
```

### 禁止事項

- 認証機能（API キー・Cognito・JWT 等）の実装
- マルチ AZ / マルチリージョン構成
- CloudWatch カスタムメトリクスの emit
- CI/CD パイプラインの構築
- Terraform module 分割
- 実データ・個人情報の使用

### 不明点の対応

不明点がある場合は：
1. まず最小構成で実装し、動作確認を行う
2. 任意拡張事項（OPT-xxx）は後回しにする
3. 設計変更が必要な場合は、変更前に確認を取る

---

## 21. 確認事項

実装開始前に以下を確認すること：

| # | 確認事項 | 確認方法 |
|---|---|---|
| 1 | AWS CLI 認証が正常に動作すること | `aws sts get-caller-identity` |
| 2 | Terraform >= 1.5 がインストールされていること | `terraform version` |
| 3 | ap-northeast-1 リージョンが使用可能であること | `aws ec2 describe-availability-zones --region ap-northeast-1` |
| 4 | Amazon Managed Grafana が ap-northeast-1 で利用可能であること | AWS コンソール確認 |
| 5 | 個人 AWS アカウントで作業していること | `aws sts get-caller-identity` でアカウント ID 確認 |

---

## Dependencies & Execution Order

### User Story 依存関係

- **US1 (P1)**: Phase 3〜7 - データパイプライン（必須・最優先）
- **US2 (P2)**: Phase 8〜9 - Grafana 可視化（US1 完了後）
- **US3 (P3)**: OPT-001 - Grafana Alerting（任意・US2 完了後）
- **US4 (P4)**: Phase 11 - リソース削除（最後）

### タスク間の主要依存関係

```
T001 → T002 → T003
T001 → T004
T001 → T005 → T006 → T007 → T008
T001 → T009
T009 → T010 → T011 → T012
T007 → T013 → T014 → T015 → T016 → T017
T014 → T019 → T018
T013〜T019 → T020 → T021
T021 → T022 → T023 → T024
T022 → T025 → T026 → T027
T021 → T028 → T029
T029 + T022 → T030 → T031 → T032
T030〜T032 → T033 → T034
T034 → T035 → T036 → T037
```

### 並列実行可能なタスク

- T006、T007、T009 は並列実行可能
- T010、T011、T012 は順次実行（同一ファイルへの追記）
- T013、T014、T015 は並列実行可能（異なる `.tf` ファイル）

---

## Implementation Strategy

### MVP（最小確認目標）

1. Phase 1 + 2: 環境セットアップ
2. Phase 3: Lambda 実装
3. Phase 4 + 5: Terraform apply
4. Phase 6: API 動作確認（US1 完了）
5. **ここで一旦確認**: curl で POST → DynamoDB 保存 → Logs 出力が動作すること

### フル検証

6. Phase 7: CloudWatch 確認
7. Phase 8 + 9: Grafana 可視化（US2 完了）
8. Phase 10: 統合テスト
9. Phase 11: 削除

### 並列実行例

```bash
# Terraform ファイル定義フェーズで並列作成可能
Task: "dynamodb.tf 定義"
Task: "iam.tf (Lambda) 定義"
Task: "cloudwatch.tf 定義"
# → 3 ファイルは独立しているため並列実行可能
```
