# 支払い方法フィールド追加 設計ドキュメント

**日付**: 2026-03-19

## 概要

請求書フォームの住所フィールド直下に「支払い方法」プルダウンを追加する。
PDF出力には表示しない（Webアプリ上のみ）。

## 変更箇所

### 1. フォームHTML（住所フィールドの直後）

`<div class="form-group full">` で住所と同幅に配置。
`id="paymentMethod"` の `<select>` を追加。

選択肢：
- （空欄 / 未選択）
- クレジットカード払い
- 口座振替払い
- 請求書払い
- 電子決済払い
- QRコード払い
- その他

### 2. collectFormData()

`paymentMethod: document.getElementById('paymentMethod').value.trim()` を追加。

### 3. loadInvoice() / newInvoice() / copyInvoice()

- `loadInvoice`: `data.paymentMethod` を `#paymentMethod` にセット
- `newInvoice`: `#paymentMethod` を空欄にリセット
- `copyInvoice`: `src.paymentMethod` をセット

### 4. PDF出力

変更なし。

## スコープ外

- PDF・印刷への表示
- 支払い方法によるフィルタリング・集計
