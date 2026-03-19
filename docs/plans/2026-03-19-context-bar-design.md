# コンテキストバー 設計ドキュメント

**日付**: 2026-03-19

## 概要

顧客選択後のメインエリアに「今どの顧客を選択中か」「新規作成中か編集中か」を常時表示するコンテキストバー（`#contextBar`）を追加する。

## 表示仕様

### 位置
ツールバー（`.toolbar`）の直上に固定1行帯として挿入。

### 見た目
- 背景: `linear-gradient(135deg, rgba(233,30,99,0.15), rgba(124,58,237,0.15))`
- 左ボーダー: `3px solid #e91e63`
- 高さ: `36px`（padding 8px 20px）
- 顧客非選択時: `display:none`

### レイアウト
```
[ 👤 顧客名（白・太字）]    [ バッジ ]
```

- 左: `👤 {顧客名}` — font-weight:700, color:#fff
- 右: 状態バッジ（pill形状）
  - 新規作成中: `＋ 新規作成中` — background: rgba(255,255,255,0.15)
  - 編集中: `✏ 編集中：No.XXXX` — background: rgba(233,30,99,0.3)

## 状態更新

| タイミング | 表示 |
|-----------|------|
| `openCustomerInvoices(name)` | バー表示、顧客名セット、バッジ=「新規作成中」 |
| `newInvoice()` | バッジ=「＋ 新規作成中」（顧客選択中のみ） |
| `loadInvoice(data)` | バッジ=「✏ 編集中：No.{invoiceNumber}」 |
| `backToCustomers()` | バー非表示 |

## 変更ファイル

- `invoice.html` のみ
  - HTML: `#contextBar` div をツールバー直上に追加
  - CSS: `.context-bar` スタイル追加
  - JS: `updateContextBar(customerName, mode, invoiceNumber)` ヘルパー関数追加、各関数から呼び出し
