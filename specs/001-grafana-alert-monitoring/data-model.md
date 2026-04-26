# Data Model: 疑似設備アラート監視システム

**Phase**: 1 — Design & Contracts  
**Date**: 2026-04-25  
**Feature**: [spec.md](./spec.md) | [plan.md](./plan.md)

---

## 1. エンティティ定義

### 1.1 Alert（疑似アラートレコード）

DynamoDB テーブル `grafana-demo-alerts` に保存するデータ構造。

#### テーブル定義

| 項目 | 値 |
|---|---|
| テーブル名 | `grafana-demo-alerts` |
| パーティションキー | `alertId` (String) |
| ソートキー | なし |
| 課金モード | PAY_PER_REQUEST（オンデマンド） |
| TTL 属性 | なし（任意拡張 EXT-010 として記録） |
| GSI | なし（今回の検証スコープでは不要） |
| ストリーム | なし |

#### 属性定義

| 属性名 | DynamoDB 型 | 必須/任意 | 送信元 | 説明 | バリデーション |
|---|---|---|---|---|---|
| `alertId` | S (String) | **必須** | クライアント | アラートの一意識別子（PK） | 空文字不可 |
| `facilityId` | S (String) | **必須** | クライアント | 設備の識別子 | 空文字不可 |
| `facilityName` | S (String) | **必須** | クライアント | 設備名 | 空文字不可 |
| `severity` | S (String) | **必須** | クライアント | 重要度 | `critical` / `warning` / `info` のみ |
| `alertType` | S (String) | **必須** | クライアント | アラート種別 | 空文字不可 |
| `message` | S (String) | **必須** | クライアント | アラートメッセージ | 空文字不可 |
| `occurredAt` | S (String) | **必須** | クライアント | アラート発生日時 | ISO 8601 形式（例: `2026-04-25T10:00:00+09:00`） |
| `receivedAt` | S (String) | **必須** | Lambda（自動付与） | システム受信日時 | ISO 8601 UTC（Lambda が `datetime.utcnow().isoformat() + "Z"` で付与） |
| `source` | S (String) | 任意 | Lambda（自動付与） | データ送信元識別子 | 固定値 `"api"` |
| `status` | S (String) | 任意 | Lambda（自動付与） | アラート状態 | 固定値 `"open"`（今回の検証では open 固定） |

#### サンプルレコード（critical）

```json
{
  "alertId": "ALT-0001",
  "facilityId": "FAC-001",
  "facilityName": "第一変電所",
  "severity": "critical",
  "alertType": "temperature_high",
  "message": "温度上昇を検知しました",
  "occurredAt": "2026-04-25T10:00:00+09:00",
  "receivedAt": "2026-04-25T01:00:05Z",
  "source": "api",
  "status": "open"
}
```

#### サンプルレコード（warning）

```json
{
  "alertId": "ALT-0002",
  "facilityId": "FAC-002",
  "facilityName": "第二変電所",
  "severity": "warning",
  "alertType": "voltage_drop",
  "message": "電圧低下を検知しました",
  "occurredAt": "2026-04-25T10:05:00+09:00",
  "receivedAt": "2026-04-25T01:05:08Z",
  "source": "api",
  "status": "open"
}
```

---

## 2. 重複 alertId の扱い（upsert 動作）

| ケース | 動作 | 実装 |
|---|---|---|
| 新規 alertId | 新規レコード作成 | `put_item` で保存 |
| 既存 alertId と重複 | **既存レコードを上書き更新**（upsert） | `put_item`（条件式なし）で上書き |

条件式による重複チェック（`condition_expression="attribute_not_exists(alertId)"`）は使用しない。重複の場合はWARN ログを出力した上でそのまま上書きする（仕様: clarification Q1 → FR-002-4 参照）。

---

## 3. バリデーションルール

### 3.1 必須フィールドチェック

以下のフィールドがすべてリクエストボディに含まれ、空文字でないことを確認する：

```
REQUIRED_FIELDS = [
  "alertId", "facilityId", "facilityName",
  "severity", "alertType", "message", "occurredAt"
]
```

いずれかが欠落または空文字の場合 → `HTTP 400` + `{"error": "MISSING_FIELD", "message": "..."}`

### 3.2 severity バリデーション

```
VALID_SEVERITIES = ["critical", "warning", "info"]
```

許可値以外の場合 → `HTTP 400` + `{"error": "INVALID_SEVERITY", "message": "severity must be one of: critical, warning, info"}`

### 3.3 occurredAt フォーマットチェック

ISO 8601 形式かどうかを Python `datetime.fromisoformat()` でパースして確認する。

パース失敗の場合 → `HTTP 400` + `{"error": "INVALID_DATE_FORMAT", "message": "occurredAt must be ISO 8601 format"}`

### 3.4 JSON パースエラー

リクエストボディが JSON として解析できない場合 → `HTTP 400` + `{"error": "INVALID_JSON", "message": "Request body must be valid JSON"}`

### 3.5 空リクエスト

リクエストボディが空または null の場合 → `HTTP 400` + `{"error": "EMPTY_BODY", "message": "Request body is required"}`

---

## 4. ログエンティティ（CloudWatch Logs）

Lambda は JSON 構造化ログを CloudWatch Logs に出力する。以下がログイベントのスキーマ。

### ログエントリ共通フィールド

| フィールド名 | 型 | 説明 |
|---|---|---|
| `level` | string | ログレベル（INFO / WARN / ERROR） |
| `event` | string | イベント識別子（下記参照） |
| `alertId` | string | 処理中の alertId（存在する場合） |
| `message` | string | ログメッセージ |
| `timestamp` | string | Lambda 標準タイムスタンプ（`@timestamp`） |

### イベント識別子一覧

| `event` 値 | レベル | タイミング |
|---|---|---|
| `REQUEST_RECEIVED` | INFO | リクエスト受信・処理開始時 |
| `VALIDATION_OK` | INFO | 入力チェック成功時 |
| `STORED` | INFO | DynamoDB 保存成功時 |
| `VALIDATION_ERROR` | WARN | 入力チェックエラー時 |
| `DUPLICATE_ALERT_ID` | WARN | 同一 alertId が再送信された時（上書き保存は継続） |
| `STORE_ERROR` | ERROR | DynamoDB 保存失敗時 |
| `UNEXPECTED_ERROR` | ERROR | 予期しない例外発生時 |

### ログ出力例（JSON 形式）

**処理開始 (INFO)**:
```json
{"level": "INFO", "event": "REQUEST_RECEIVED", "alertId": "ALT-0001", "message": "Request received"}
```

**保存成功 (INFO)**:
```json
{"level": "INFO", "event": "STORED", "alertId": "ALT-0001", "message": "Alert stored successfully"}
```

**入力エラー (WARN)**:
```json
{"level": "WARN", "event": "VALIDATION_ERROR", "alertId": null, "field": "severity", "value": "high", "message": "severity must be one of: critical, warning, info"}
```

**DynamoDB エラー (ERROR)**:
```json
{"level": "ERROR", "event": "STORE_ERROR", "alertId": "ALT-0001", "error_code": "ProvisionedThroughputExceededException", "message": "Failed to store alert"}
```

---

## 5. CloudWatch Logs Insights クエリスキーマ

JSON 構造化ログを前提とした Logs Insights クエリで参照するフィールド：

| フィールド | 型 | 用途 |
|---|---|---|
| `@timestamp` | timestamp | 時系列フィルタ |
| `level` | string | エラーフィルタ（`level = "ERROR"`） |
| `event` | string | イベント種別フィルタ |
| `alertId` | string | 特定アラートの追跡 |

severity 別件数集計は、リクエストボディ内の `severity` フィールドをログに含める場合のみ可能になる。ログ出力仕様で `REQUEST_RECEIVED` 時に severity を含めること（詳細: [contracts/api.md](./contracts/api.md)）。

---

## 6. 状態遷移

今回の検証スコープでは `status` は常に `"open"` 固定。以下は将来拡張（EXT-005）時の参考：

```
[open] → [closed]  (手動または自動クローズ)
```

---

## 7. DynamoDB 設計判断メモ

| 項目 | 決定 | 理由 |
|---|---|---|
| ソートキー | なし | 1 アラート 1 レコードの単純構造。複合クエリ不要 |
| GSI | なし | facilityId や severity による検索はスコープ外 |
| TTL | なし | 検証後はテーブルごと削除するため不要。長期保管が必要になれば追加 |
| 属性型 | String のみ | 日時を String で保存（ISO 8601 文字列）。DynamoDB の日時型は存在しない |
| オンデマンド | 使用 | 検証規模（数百件）でプロビジョンドの最低料金を払うのは割高 |
