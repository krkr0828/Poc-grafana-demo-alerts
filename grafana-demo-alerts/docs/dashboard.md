# Grafana ダッシュボード `Pseudo Facility Alert Monitoring`

Amazon Managed Grafana 上で構築する、疑似設備アラート監視ダッシュボードの構成・作成手順・復元手順をまとめる。

## 概要

| 項目 | 値 |
|---|---|
| ダッシュボード名 | `Pseudo Facility Alert Monitoring` |
| データソース | CloudWatch（`AWS SDK Default` 認証）|
| 対象リージョン | `ap-northeast-1` |
| パネル数 | 8（メトリクス 6 + Logs Insights 2）|
| 時間範囲 | デフォルト Last 1 hour |

## パネル構成

### メトリクス系（CloudWatch Metrics クエリ）

| # | タイトル | Visualization | Namespace | Metric | Statistic | Dimensions |
|---|---|---|---|---|---|---|
| 1 | API リクエスト数 | Time series | AWS/ApiGateway | `Count` | Sum | `ApiId` |
| 2 | API エラー数 (4xx/5xx) | Time series | AWS/ApiGateway | `4xx` / `5xx`（2 クエリ）| Sum | `ApiId` |
| 3 | Lambda 実行回数 | Stat | AWS/Lambda | `Invocations` | Sum | `FunctionName` |
| 4 | Lambda エラー数 | Stat | AWS/Lambda | `Errors` | Sum | `FunctionName` |
| 5 | Lambda 実行時間 (ms) | Time series | AWS/Lambda | `Duration` | **Average** | `FunctionName` |
| 6 | DynamoDB 書き込み (WCU) | Time series | AWS/DynamoDB | `ConsumedWriteCapacityUnits` | Sum | `TableName` |

> HTTP API（API Gateway V2）のエラーメトリクスは小文字の `4xx` / `5xx`。REST API の `4XXError` / `5XXError` ではない。

### Logs Insights 系（CloudWatch Logs クエリ）

すべて Log Group: `/aws/lambda/grafana-demo-alert-handler` を参照。

#### パネル 7: アラート総件数（Stat）

```
fields @timestamp, @message
| filter @message like /STORED/
| stats count() as total_alerts
```

正常受信完了（DynamoDB 保存成功）件数を Stat 表示する。

#### パネル 8: severity 別アラート件数（Bar chart）

```
fields @timestamp, severity, event
| filter event = "REQUEST_RECEIVED"
| stats count() as cnt by severity
```

リクエスト受信時の severity 別件数を集計する。CloudWatch Logs Insights は JSON ログを自動展開するため、`severity` フィールドへ直接アクセスできる。

## 作成手順サマリ

1. Grafana 左サイドバー → Dashboards → New → New dashboard
2. 「+ Add visualization」→ データソース `CloudWatch` を選択
3. 上記パネル構成表に従って 1 パネルずつ作成、各パネル設定後に「Apply」
4. 全 8 パネル作成後、ダッシュボード名 `Pseudo Facility Alert Monitoring` で保存
5. 時間範囲を Last 1 hour に設定

## JSON エクスポートからの復元手順

新規 Grafana ワークスペースに同じダッシュボードを再現する場合：

1. Grafana 左サイドバー → Dashboards → New → **Import**
2. 「Upload dashboard JSON file」で `docs/dashboard-export.json` を選択
3. 表示された Import 画面で：
   - Name: そのまま（または変更）
   - Folder: 任意
   - **CloudWatch** データソース選択（事前に T029 の手順で CloudWatch DataSource を作成しておくこと）
4. 「Import」

> エクスポート時に「Export for sharing externally」を ON にしているため、データソース名は変数参照に変換されている。Import 時に既存の CloudWatch データソースを指定すれば動作する。

### JSON バリデーション

```bash
python3 -m json.tool grafana-demo-alerts/docs/dashboard-export.json > /dev/null && echo "OK"
```

## トラブルシューティング

| 症状 | 想定原因 | 対処 |
|---|---|---|
| 全パネル No data | 時間範囲不一致 | 右上時間範囲を Last 1 hour に |
| パネル 2 で Dimension 値が出ない | メトリクス名が REST API 形式 | `4XXError` → `4xx`、`5XXError` → `5xx` に修正 |
| パネル 5 だけ値が大きすぎる | Statistic が Sum になっている | Average に変更 |
| パネル 8 が 1 行だけ | Visualization が Stat | Bar chart に変更 |
| Logs Insights パネル空 | Log Group 未選択 / 自動補完候補から確定していない | 候補から Enter で確定 |
| Save & test 失敗 | Grafana IAM ロールに CloudWatch 権限なし | `terraform/iam.tf` の grafana ポリシーアタッチを確認 |

## 任意拡張：Grafana Alerting の追加メモ

将来的にアラート通知を組み込む場合の起点メモ（本タスク範囲外）：

1. 各パネルの編集画面 → 「**Alert**」タブ → New alert rule
2. Evaluation: 例えば「Lambda Errors > 0 が 5 分継続」
3. Contact point として Webhook / Email / Slack を Grafana 内で設定
4. Notification policy で重要度別ルーティング

> Managed Grafana で SNS / SES を使う場合は IAM ロールへの権限追加が別途必要。

## 関連リソース ID（2026-04-30 apply 時点）

- Grafana Workspace: `g-0a7afe9959`
- Workspace URL: `https://g-0a7afe9959.grafana-workspace.ap-northeast-1.amazonaws.com`
- API Gateway ApiId: `8ddkagusye`
- Lambda Function: `grafana-demo-alert-handler`
- DynamoDB Table: `grafana-demo-alerts`
- Log Group: `/aws/lambda/grafana-demo-alert-handler`

> リソース ID は `terraform apply` のたびに変わるため、上記は記録時点のもの。最新値は `terraform output` で確認すること。
