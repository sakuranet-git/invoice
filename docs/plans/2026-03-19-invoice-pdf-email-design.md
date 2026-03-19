# 請求書PDF生成・メール添付 設計ドキュメント

**Date:** 2026-03-19

## Goal

請求書をA4対応のHTMLレイアウトで生成し、PDFとしてメールに添付して送信できるようにする。電子印鑑はドラッグで自由に配置可能。

---

## アーキテクチャ

**変更ファイル:**
- `invoice.html` — フォーム追加・印刷エリア改修・PDF生成ロジック追加
- `invoice_send.php` — PDF添付対応（multipart MIME）

**追加ライブラリ:**
- `html2pdf.js` CDN（`<script>` 1行追加のみ）

**フロー:**
1. フォーム入力（請求対象月を選択）
2. 「メール送信」クリック
3. `#printArea` に請求書HTMLを生成
4. A4プレビューモーダルが開く（印鑑ドラッグ可能）
5. html2pdf.js → PDFを生成（A4）
6. PDFをbase64に変換 → `invoice_send.php` にPOST
7. PHP: multipart MIMEメール + PDF添付ファイル送信

---

## UI変更詳細

### フォーム変更
- 「支払期限」フィールドを削除
- 「請求対象月」年月ドロップダウン追加（例: `2026年3月分`）
- デフォルト: 請求日の前月（月初～15日は前月、16日～は当月）

### A4レイアウト
- A4固定幅（794px = 210mm相当）
- 余白: 上15mm、左右20mm、下15mm
- 「〇〇年〇月分」をヘッダーに表示（支払期限の代わり）
- 品目が多い場合は2ページ目に自動改ページ（`page-break-inside: avoid`）

### 電子印鑑ドラッグ（必須）
- 会社印・個人印の2つを独立してドラッグ移動可能
- `position: absolute` で配置、`mousedown/mousemove/mouseup` でドラッグ
- 配置位置を `localStorage` に保存（次回起動時も維持）
- PDF生成時はその配置位置でPDF化

### プレビューモーダル
- 「メール送信」クリック → A4プレビューモーダルが先に表示
- プレビュー上で印鑑を移動 → 「このPDFを添付して送信」クリック
- 宛先・件名・本文の確認 → 「送信する」で完了

---

## PDF生成技術詳細

```js
html2pdf().set({
    margin: [15, 20, 15, 20],  // mm: top, right, bottom, left
    filename: `請求書_${year}${month}_${invNumber}.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
})
```

---

## invoice_send.php 変更点

- リクエストに `pdf_base64` と `pdf_filename` を追加受付
- `multipart/mixed` MIMEで本文＋PDF添付を送信
- 既存のテキスト本文はそのまま維持
- バックアップ: `「🖨 印刷/PDF保存」` ボタン（既存）も継続提供

---

## Firestore データ変更

| フィールド | 変更 |
|---|---|
| `invDueDate` | 削除（フォーム・保存・表示から除去） |
| `billingMonth` | 追加（例: `"2026-03"`） |
