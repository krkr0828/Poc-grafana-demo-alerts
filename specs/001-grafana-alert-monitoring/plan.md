# Implementation Plan: 疑似設備アラート監視システム

**Branch**: `001-grafana-alert-monitoring` | **Date**: 2026-04-25 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/001-grafana-alert-monitoring/spec.md`

## Summary

AWS 上に Terraform で構築する個人検証用の疑似設備アラート監視システム。API Gateway HTTP API → Lambda (Python 3.12) → DynamoDB のデータパイプラインと、CloudWatch → Amazon Managed Grafana の可視化パイプラインを最小構成で実装する。検証後に `terraform destroy` で全 AWS リソースを削除できることを前提とした低コスト・短時間設計。

## Technical Context

**Language/Version**: Python 3.12 (Lambda runtime)、HCL (Terraform >= 1.5)  
**Primary Dependencies**: boto3 (AWS SDK for Python)、hashicorp/aws provider ~> 5.0  
**Storage**: DynamoDB オンデマンド課金、CloudWatch Logs (保持期間 3 日)  
**Testing**: curl / HTTP クライアントによる手動統合テスト、terraform fmt / validate / plan  
**Target Platform**: AWS ap-northeast-1（API Gateway HTTP API + Lambda + DynamoDB + Managed Grafana）  
**Project Type**: AWS IaC (Terraform) + Lambda アプリケーション + 監視ダッシュボード  
**Performance Goals**: 数十〜数百件の疑似アラート POST が処理できれば十分（高負荷試験不要）  
**Constraints**: 総コスト約 15 USD 以内、検証時間 2 時間以内、東京リージョン固定、単独利用  
**Scale/Scope**: 個人検証（1 ユーザー）、短期稼働、検証後削除前提

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

プロジェクト固有の Constitution は未定義（テンプレートのみ）。ゲート違反なし。

本プロジェクトの実装ガイドラインとして以下の原則を適用する：

| 原則 | 内容 |
|---|---|
| シンプルさ優先 | 過剰設計をしない。検証目的に必要な最小構成のみ実装する |
| 削除容易性 | すべての AWS リソースは `terraform destroy` で削除できること |
| コスト意識 | 標準メトリクス活用・カスタムメトリクス不使用・ログ保持期間最小化 |
| 再現性 | Terraform で環境を再現できること（state は local backend） |
| 学習優先 | Grafana ダッシュボード作成は GUI 手動操作を許容する |

**Phase 1 再チェック結果**: 設計後に violations なし。

## Project Structure

### Documentation (this feature)

```text
specs/001-grafana-alert-monitoring/
├── plan.md              # This file
├── research.md          # Phase 0: 技術決定・設計根拠
├── data-model.md        # Phase 1: DynamoDB スキーマ・エンティティ定義
├── quickstart.md        # Phase 1: 構築・確認・削除手順
├── contracts/
│   └── api.md           # Phase 1: API 仕様
└── tasks.md             # Phase 2: /speckit-tasks コマンド出力（未作成）
```

### Source Code (repository root)

```text
grafana-demo-alerts/
├── README.md
├── terraform/
│   ├── providers.tf       # AWS provider, required_providers, terraform block
│   ├── variables.tf       # 変数定義（region, project_name, log_retention 等）
│   ├── outputs.tf         # API URL, Lambda 名, DynamoDB 名, Grafana endpoint 等
│   ├── main.tf            # local values, common tags
│   ├── iam.tf             # Lambda 実行ロール, Grafana 用 IAM ロール/ポリシー
│   ├── lambda.tf          # Lambda 関数, Lambda permission, archive_file data source
│   ├── apigateway.tf      # HTTP API, route, integration, stage
│   ├── dynamodb.tf        # DynamoDB テーブル
│   ├── cloudwatch.tf      # CloudWatch Logs ロググループ, 保持期間設定
│   └── grafana.tf         # Managed Grafana Workspace
├── lambda/
│   └── handler.py         # Lambda ハンドラー (Python 3.12)
├── samples/
│   ├── alert-critical.json
│   ├── alert-warning.json
│   └── alert-info.json
└── docs/
    ├── dashboard.md       # Grafana ダッシュボード作成・JSON エクスポート手順
    └── cleanup.md         # リソース削除確認手順
```

**Structure Decision**: IaC（Terraform）と Lambda ソースを分離したフラット構成。モジュール分割は行わない。Terraform ファイルはリソース種別単位で分割することで、可読性と削除時の把握容易性を確保する。

## Complexity Tracking

Constitution 違反なし。追記不要。
