# API Contract: 疑似設備アラート監視システム

**Phase**: 1 — Design & Contracts  
**Date**: 2026-04-25  
**Feature**: [spec.md](../spec.md) | [data-model.md](../data-model.md)

---

## 1. エンドポイント概要

| 項目 | 内容 |
|---|---|
| 種別 | AWS API Gateway HTTP API |
| Base URL | `https://{api-id}.execute-api.ap-northeast-1.amazonaws.com` |
| Stage | `$default`（デフォルトステージ） |
| Method | `POST` |
| Path | `/alerts` |
| Content-Type | `application/json` |
| 認証 | なし（検証用途のため） |
| CORS | 不要（curl からのリクエストのみ） |

**完全 URL 例**:
```
POST https://{api-id}.execute-api.ap-northeast-1.amazonaws.com/alerts
```

---

## 2. リクエスト仕様

### 2.1 ヘッダー

| ヘッダー名 | 値 | 必須/任意 |
|---|---|---|
| `Content-Type` | `application/json` | 必須 |

### 2.2 リクエストボディ

| フィールド名 | 型 | 必須/任意 | 説明 | バリデーション |
|---|---|---|---|---|
| `alertId` | string | **必須** | アラートの一意識別子 | 空文字不可 |
| `facilityId` | string | **必須** | 設備の識別子 | 空文字不可 |
| `facilityName` | string | **必須** | 設備名 | 空文字不可 |
| `severity` | string | **必須** | 重要度 | `critical` / `warning` / `info` のみ |
| `alertType` | string | **必須** | アラート種別（任意の文字列） | 空文字不可 |
| `message` | string | **必須** | アラートメッセージ | 空文字不可 |
| `occurredAt` | string | **必須** | アラート発生日時 | ISO 8601 形式（例: `2026-04-25T10:00:00+09:00`） |

### 2.3 リクエスト例（critical）

```bash
curl -X POST https://{api-id}.execute-api.ap-northeast-1.amazonaws.com/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "alertId": "ALT-0001",
    "facilityId": "FAC-001",
    "facilityName": "第一変電所",
    "severity": "critical",
    "alertType": "temperature_high",
    "message": "温度上昇を検知しました",
    "occurredAt": "2026-04-25T10:00:00+09:00"
  }'
```

### 2.4 リクエスト例（warning）

```bash
curl -X POST https://{api-id}.execute-api.ap-northeast-1.amazonaws.com/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "alertId": "ALT-0002",
    "facilityId": "FAC-002",
    "facilityName": "第二変電所",
    "severity": "warning",
    "alertType": "voltage_drop",
    "message": "電圧低下を検知しました",
    "occurredAt": "2026-04-25T10:05:00+09:00"
  }'
```

### 2.5 リクエスト例（info）

```bash
curl -X POST https://{api-id}.execute-api.ap-northeast-1.amazonaws.com/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "alertId": "ALT-0003",
    "facilityId": "FAC-003",
    "facilityName": "第三変電所",
    "severity": "info",
    "alertType": "status_change",
    "message": "設備状態の変更を検知しました",
    "occurredAt": "2026-04-25T10:10:00+09:00"
  }'
```

---

## 3. レスポンス仕様

### 3.1 正常レスポンス（HTTP 200）

| フィールド名 | 型 | 説明 |
|---|---|---|
| `message` | string | 処理結果メッセージ（固定値: `"alert accepted"`） |
| `alertId` | string | 受け付けた alertId |
| `stored` | boolean | DynamoDB 保存成功フラグ（常に `true`） |

**レスポンス例**:
```json
{
  "message": "alert accepted",
  "alertId": "ALT-0001",
  "stored": true
}
```

### 3.2 エラーレスポンス共通形式

全エラーレスポンスは以下の JSON 構造とする（clarification Q3 決定）：

```json
{
  "error": "ERROR_CODE",
  "message": "エラーの説明文"
}
```

---

## 4. エラーレスポンス一覧

### 4.1 JSON 形式不正（HTTP 400）

```json
{
  "error": "INVALID_JSON",
  "message": "Request body must be valid JSON"
}
```

**発生条件**: リクエストボディが JSON としてパースできない場合

---

### 4.2 空リクエスト（HTTP 400）

```json
{
  "error": "EMPTY_BODY",
  "message": "Request body is required"
}
```

**発生条件**: リクエストボディが空または null の場合

---

### 4.3 必須項目不足（HTTP 400）

```json
{
  "error": "MISSING_FIELD",
  "message": "Required field 'severity' is missing or empty"
}
```

**発生条件**: 必須フィールド（alertId / facilityId / facilityName / severity / alertType / message / occurredAt）のいずれかが存在しない、または空文字の場合

---

### 4.4 severity 不正（HTTP 400）

```json
{
  "error": "INVALID_SEVERITY",
  "message": "severity must be one of: critical, warning, info"
}
```

**発生条件**: severity の値が `critical` / `warning` / `info` 以外の場合

---

### 4.5 occurredAt 形式不正（HTTP 400）

```json
{
  "error": "INVALID_DATE_FORMAT",
  "message": "occurredAt must be ISO 8601 format (e.g., 2026-04-25T10:00:00+09:00)"
}
```

**発生条件**: occurredAt が ISO 8601 形式でない場合

---

### 4.6 alertId 重複（HTTP 200）

重複 alertId が送信された場合は**エラーとせず、既存レコードを上書き更新**（upsert 動作）する。  
レスポンスは通常の HTTP 200 と同じ。WARN ログ（`DUPLICATE_ALERT_ID`）を CloudWatch Logs に出力する。

```json
{
  "message": "alert accepted",
  "alertId": "ALT-0001",
  "stored": true
}
```

---

### 4.7 DynamoDB 保存失敗（HTTP 500）

```json
{
  "error": "STORE_ERROR",
  "message": "Failed to store alert. Please try again."
}
```

**発生条件**: DynamoDB の `put_item` 処理が例外で失敗した場合  
**補足**: 詳細なエラー情報は CloudWatch Logs（`STORE_ERROR` イベント）に出力する

---

### 4.8 予期しない例外（HTTP 500）

```json
{
  "error": "INTERNAL_ERROR",
  "message": "An unexpected error occurred."
}
```

**発生条件**: 上記以外の未捕捉例外が発生した場合  
**補足**: スタックトレースは CloudWatch Logs（`UNEXPECTED_ERROR` イベント）に出力する

---

## 5. Lambda 処理フロー（疑似コード）

```
def handler(event, context):
    try:
        # 1. リクエストボディ取得
        body = event.get("body")
        if not body:
            return 400, {"error": "EMPTY_BODY", ...}

        # 2. JSON パース
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return 400, {"error": "INVALID_JSON", ...}

        # 3. 必須フィールドチェック
        for field in REQUIRED_FIELDS:
            if not data.get(field):
                return 400, {"error": "MISSING_FIELD", "message": f"Required field '{field}' is missing or empty"}

        # 4. severity チェック
        if data["severity"] not in VALID_SEVERITIES:
            return 400, {"error": "INVALID_SEVERITY", ...}

        # 5. occurredAt フォーマットチェック
        try:
            datetime.fromisoformat(data["occurredAt"])
        except ValueError:
            return 400, {"error": "INVALID_DATE_FORMAT", ...}

        # 6. receivedAt 付与
        data["receivedAt"] = datetime.utcnow().isoformat() + "Z"
        data["source"] = "api"
        data["status"] = "open"

        # 7. DynamoDB 保存（upsert）
        log INFO STORED
        table.put_item(Item=data)

        # 8. 正常レスポンス
        return 200, {"message": "alert accepted", "alertId": data["alertId"], "stored": True}

    except ClientError as e:
        log ERROR STORE_ERROR
        return 500, {"error": "STORE_ERROR", ...}
    except Exception as e:
        log ERROR UNEXPECTED_ERROR
        return 500, {"error": "INTERNAL_ERROR", ...}
```

---

## 6. 環境変数

Lambda 関数が使用する環境変数：

| 変数名 | 説明 | 例 |
|---|---|---|
| `TABLE_NAME` | DynamoDB テーブル名 | `grafana-demo-alerts` |
| `LOG_LEVEL` | ログレベル | `INFO` |

---

## 7. Terraform 出力値（API エンドポイント）

`terraform apply` 後に以下が出力される：

```hcl
output "api_endpoint" {
  value = "${aws_apigatewayv2_api.main.api_endpoint}/alerts"
  description = "疑似アラート受信 API のエンドポイント URL"
}
```

**curl での使用例**:
```bash
API_ENDPOINT=$(terraform output -raw api_endpoint)
curl -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d @samples/alert-critical.json
```
