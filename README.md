# Poc-grafana-demo-alerts

Amazon Managed Grafana 学習用 PoC: **疑似設備アラート監視システム**

API Gateway → Lambda → DynamoDB → CloudWatch → Amazon Managed Grafana の最小構成で、AWS 上の業務システム監視・可視化を Terraform で構築する個人検証プロジェクトです。

---

## 検証目的

1. Amazon Managed Grafana の基本操作習得
2. CloudWatch をデータソースとした AWS 監視ダッシュボード設計の理解
3. API Gateway / Lambda / DynamoDB の標準メトリクス可視化
4. Terraform による IaC 構築と削除容易性の検証

---

## リポジトリ構成

```
.
├── specs/001-grafana-alert-monitoring/
│   ├── spec.md            要件定義書
│   ├── plan.md            実装計画
│   ├── research.md        技術判断
│   ├── data-model.md      データモデル
│   ├── contracts/api.md   API 仕様
│   ├── quickstart.md      検証手順
│   └── tasks.md           実装タスク（37 タスク / 11 フェーズ）
└── grafana-demo-alerts/   実装本体（後続タスクで作成）
    ├── terraform/         Terraform 定義
    ├── lambda/            Lambda ソース
    ├── samples/           疑似アラートサンプル
    └── docs/              手動設定手順
```

---

## 前提条件

- AWS CLI 設定済み
- Terraform >= 1.5
- Python 3.x
- AWS リージョン: `ap-northeast-1`

---

## 検証時の注意

- 検証完了後は `terraform destroy` で**必ず**リソースを削除すること
- Amazon Managed Grafana は最低料金（約 $9/月）が固定発生
- 実データ・個人情報は扱わない（疑似データのみ）
- API エンドポイントは認証なしのため、長時間稼働させない

---

## ステータス

🚧 設計完了 → 実装フェーズ開始予定
