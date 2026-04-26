# Research: 疑似設備アラート監視システム

**Phase**: 0 — Outline & Research  
**Date**: 2026-04-25  
**Feature**: [spec.md](./spec.md) | [plan.md](./plan.md)

---

## 技術決定一覧

### Decision 1: API Gateway の種別

**Decision**: HTTP API（REST API ではなく）を使用する  
**Rationale**: HTTP API は REST API と比較してコストが約 71% 安く（$1.00/100万リクエスト vs $3.50）、Lambda 統合のセットアップが簡単。今回は API キー認証・WAF・使用量プランなどの REST API 固有機能を使用しないため HTTP API で十分。  
**Alternatives considered**:
- REST API: 機能豊富だがコスト高。本検証で不要な機能が多い。
- ALB (Application Load Balancer): EC2 が不要な本構成には不向き。

---

### Decision 2: DynamoDB の課金モード

**Decision**: オンデマンド（PAY_PER_REQUEST）を使用する  
**Rationale**: 検証用途のため、リクエスト数が事前に読めない。プロビジョンドキャパシティは最低料金が発生し続けるため、数十〜数百件の疑似データ送信には割高になる。オンデマンドは実際に使った分だけ課金されるため個人検証に適している。  
**Alternatives considered**:
- プロビジョンドキャパシティ: 安定した大量リクエストには適するが、今回の規模では不向き。

---

### Decision 3: CloudWatch をデータソースとして Grafana に使う理由

**Decision**: CloudWatch をデータソースとして Amazon Managed Grafana に接続する  
**Rationale**:
- API Gateway / Lambda / DynamoDB の標準メトリクスは CloudWatch に自動蓄積される（追加設定不要）
- CloudWatch Logs Insights を使うことで、ログから業務イベント件数（severity 別アラート数等）を集計できる
- Managed Grafana の CloudWatch データソースプラグインが標準で利用可能
- 他のデータソース（Prometheus, Timestream 等）は追加インフラが必要になり、今回のスコープ外  
**Alternatives considered**:
- Amazon Managed Service for Prometheus: メトリクス収集用エージェントが必要で構成が複雑になる。
- Datadog / New Relic: 外部 SaaS で追加コスト発生。今回の学習目標（AWS サービス理解）に合わない。

---

### Decision 4: CloudWatch カスタムメトリクスを原則使用しない理由

**Decision**: カスタムメトリクスは使用せず、標準メトリクス + CloudWatch Logs Insights で対応する  
**Rationale**:
- CloudWatch カスタムメトリクスは 1 メトリクスあたり $0.30/月かかる（標準メトリクスは無料）
- severity 別件数の集計は Logs Insights クエリで実現でき、コストが大幅に抑えられる
- 個人検証レベルでは Logs Insights の応答速度で十分
- 将来的に実案件でリアルタイム集計が必要になった場合のみカスタムメトリクス化を検討する  
**Alternatives considered**:
- Lambda から `put_metric_data` で severity 別カスタムメトリクスを emit: Grafana での扱いがシンプルになるが、コスト増。任意拡張として残す（EXT-007）。

---

### Decision 5: Grafana Alerting を任意扱いにする理由

**Decision**: Grafana Alerting は任意検証とする（必須スコープから外す）  
**Rationale**:
- 通知先（メール/Slack）の設定・管理は本検証の主目的（Grafana 操作・可視化理解）の外側にある
- アラートルール設定は Grafana ダッシュボード作成が完了した後のステップとして十分
- 通知先なし（Grafana UI 上の Firing 確認のみ）であれば実装コストは低いが、時間内に到達できない可能性がある
- P1（データパイプライン）とP2（可視化）が完成してから取り組めばよい  
**Alternatives considered**:
- SNS 通知先設定: 追加コストと設定ステップが増える。本検証の優先事項ではない。

---

### Decision 6: AWS リソースを Terraform で管理する理由

**Decision**: すべての AWS リソースを Terraform（local backend）で管理する  
**Rationale**:
- 検証後に `terraform destroy` 1 コマンドで全リソースを確実に削除できる
- 手動でリソースを作成すると削除漏れのリスクが高まり、意図しない継続課金が発生する
- local backend はバックエンドサーバー設定不要で個人検証に最適
- Terraform コードが将来の IaC 移行・実案件応用時の参考資料になる  
**Alternatives considered**:
- CloudFormation: AWS ネイティブだが、Terraform の方が本人の学習目標（Terraform 検証）に合致。
- 手動（AWS コンソール）: 削除漏れリスクが高く、再現性がない。

---

### Decision 7: Grafana ダッシュボードの手動設定を許容する理由

**Decision**: Grafana ダッシュボード作成は GUI 手動操作を許容し、Terraform 管理を必須としない  
**Rationale**:
- 本検証の主目的の一つが「Grafana の基本操作を理解する」こと
- GUI でパネルを操作することで Grafana のクエリエディタ・データソース設定・ビジュアル設定を体験できる
- JSON エクスポートを行うことで後から Terraform（grafana_dashboard リソース）への移行も可能
- ダッシュボードを Terraform で先に定義すると GUI 操作の学習機会が失われる  
**Alternatives considered**:
- grafana_dashboard リソースで Terraform 管理: 再現性は高いが、GUI 操作を学ぶ本来の目的に反する。任意拡張（EXT-001）として残す。

---

### Decision 8: Grafana 認証方式

**Decision**: Grafana 組み込み認証（username / password）を使用する  
**Rationale**: IAM Identity Center は個人 AWS アカウントでの初期セットアップが複雑（別サービスの有効化・ユーザー作成が必要）。組み込み認証は Managed Grafana ワークスペース作成後すぐに Admin ユーザーを設定できるため、検証時間内に完結しやすい。  
**Source**: clarification Q1 (2026-04-25)

---

### Decision 9: Lambda ランタイム

**Decision**: Python 3.12 を使用する  
**Rationale**: 最新の AWS Lambda でサポートされているランタイムであり、boto3 が標準で利用可能。Python は Lambda + DynamoDB 操作の一般的な選択肢で、サンプルコードが豊富。  
**Alternatives considered**:
- Node.js 20: 同等の選択肢だが、Python の方が DynamoDB 操作の可読性が高い。
- Go: 起動が速いが、Lambda の検証目的ではランタイム性能は優先事項ではない。

---

### Decision 10: ダッシュボード管理方法

**Decision**: GUI で作成後、JSON エクスポートして保存する  
**Rationale**: GUI 操作で Grafana を学習しつつ、JSON エクスポートにより再現性・IaC 準備ができる。エクスポートした JSON は `docs/dashboard.md` または専用 JSON ファイルとしてリポジトリに保存する。  
**Source**: clarification Q2 (2026-04-25)

---

### Decision 11: エラーレスポンス形式

**Decision**: バリデーションエラー時は構造化 JSON を返す（`{"error": "ERROR_CODE", "message": "説明"}`）  
**Rationale**: curl での検証時にエラー内容が確認しやすい。実案件でも使いやすい形式。HTTP ステータスコード + JSON ボディで種別・原因を明示する。  
**Source**: clarification Q3 (2026-04-25)

---

## Terraform Provider バージョン

| Provider | Version Constraint | 備考 |
|---|---|---|
| hashicorp/aws | ~> 5.0 | Managed Grafana リソース対応済み |
| hashicorp/archive | ~> 2.0 | Lambda ZIP パッケージング用 |

## 主要 Terraform リソース一覧

| リソース種別 | Terraform リソース名 | 管理方法 |
|---|---|---|
| DynamoDB テーブル | `aws_dynamodb_table` | Terraform |
| Lambda 関数 | `aws_lambda_function` | Terraform |
| Lambda 実行ロール | `aws_iam_role` (lambda) | Terraform |
| Lambda IAM ポリシー | `aws_iam_role_policy` | Terraform |
| Lambda permission | `aws_lambda_permission` | Terraform |
| CloudWatch Logs グループ | `aws_cloudwatch_log_group` | Terraform |
| API Gateway HTTP API | `aws_apigatewayv2_api` | Terraform |
| API Gateway route | `aws_apigatewayv2_route` | Terraform |
| API Gateway integration | `aws_apigatewayv2_integration` | Terraform |
| API Gateway stage | `aws_apigatewayv2_stage` | Terraform |
| Managed Grafana ワークスペース | `aws_grafana_workspace` | Terraform |
| Grafana IAM ロール | `aws_iam_role` (grafana) | Terraform |
| Grafana IAM ポリシー | `aws_iam_role_policy` | Terraform |
| Grafana Data Source 設定 | - | **手動** |
| Grafana ダッシュボード | - | **手動** (JSON エクスポートで保存) |
| Grafana Alerting ルール | - | **手動**（任意） |

## 未解決事項（Deferred to Tasks）

- Lambda ソースコードの具体的な実装（handler.py）は `/speckit-tasks` → 実装フェーズで対応
- Grafana ダッシュボードの具体的なパネル JSON は手動作成後にエクスポートして保存
- サンプルデータ JSON ファイル（samples/）の具体的な内容はタスクで作成
