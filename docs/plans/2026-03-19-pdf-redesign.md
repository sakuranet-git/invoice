# 請求書PDFデザインリデザイン 実装プラン

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** PDFプレビューのデザインをSAKURAブランドのグラデーション（ピンク→パープル）で刷新し、消えていた登録番号T9120001205370を復活させる。

**Architecture:** `invoice.html` 内の `.pi-*` CSS ブロック全体を置き換え、`buildInvoiceHTML()` のHTML構造を更新する。`COMPANY_REG_NUMBER` 定数を追加して `pi-our-side` に表示する。変更ファイルは `invoice.html` のみ。

**Tech Stack:** Vanilla JS, HTML/CSS（グラデーション, `-webkit-background-clip`）, Noto Sans JP / Outfit フォント

---

### Task 1: COMPANY_REG_NUMBER 定数を追加

**Files:**
- Modify: `C:\Users\MYPC\Development\請求書\invoice.html` (line ~929, STAMP_CO_B64 等の定数の直後)

**Step 1: 定数を追加**

`let db;`（line 934）の直前に以下を挿入する。
既存の `const LOGO_B64 = ...;` の行末の後ろを探して編集する。

```js
    /** インボイス制度登録番号（固定） */
    const COMPANY_REG_NUMBER = 'T9120001205370';
```

正確な挿入位置:
```
    const LOGO_B64      = 'data:image/jpeg;base64,...';   ← この行の直後

    /** インボイス制度登録番号（固定） */
    const COMPANY_REG_NUMBER = 'T9120001205370';

    /** @type {firebase.firestore.Firestore} */
    let db;
```

**Step 2: 確認**

ブラウザで `invoice.html` を開き、コンソールに `COMPANY_REG_NUMBER` と入力して `'T9120001205370'` が返ることを確認。

**Step 3: コミットしない**（Task 2・3 と合わせて最後にまとめてコミット）

---

### Task 2: `.pi-*` CSS ブロックを全面置き換え

**Files:**
- Modify: `C:\Users\MYPC\Development\請求書\invoice.html` (line 450〜580)

**Step 1: 置き換え範囲を特定**

現在の `.pi-page {` から `.pi-page-break` の直前までを置き換える。

old_string（開始マーカー）:
```
        .pi-page {
```
old_string（終了マーカー直前まで、`.pi-note` ブロックの `}` まで）:
```
        .pi-note {
            margin-top: 12px;
            padding: 8px 12px;
            border: 1px solid #bbb;
            border-left: 3px solid #555;
            font-size: 11px;
            color: #444;
            line-height: 1.8;
        }
```

**Step 2: 新しいCSSに置き換え**

以下のCSSブロック全体で置き換える:

```css
        .pi-page {
            font-family: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', sans-serif;
            color: #111;
            background: #fff;
            width: 794px;
            min-height: 1123px;
            font-size: 12px;
            line-height: 1.5;
            position: relative;
            box-sizing: border-box;
            padding: 0;
        }

        /* ---- トップグラデーションバー ---- */
        .pi-header-bar {
            height: 8px;
            background: linear-gradient(135deg, #e91e63, #7c3aed);
            width: 100%;
            margin-bottom: 0;
        }

        /* ---- コンテンツラッパー ---- */
        .pi-content {
            padding: 20px 56px 40px;
        }

        /* ---- ヘッダー行 ---- */
        .pi-head-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 16px;
        }
        .pi-head-left { display: flex; align-items: center; gap: 14px; }

        /* ---- 請求書タイトル ---- */
        .pi-title-accent {
            width: 4px;
            height: 44px;
            background: linear-gradient(180deg, #e91e63, #7c3aed);
            border-radius: 2px;
            flex-shrink: 0;
        }
        .pi-title-box {
            font-family: 'Outfit', sans-serif;
            font-size: 26px;
            font-weight: 900;
            letter-spacing: 8px;
            background: linear-gradient(135deg, #e91e63, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .pi-head-right { text-align: right; font-size: 11px; color: #555; line-height: 2.2; }
        .pi-billing-month { font-size: 14px; font-weight: 900; color: #e91e63; }

        /* ---- 顧客 / 自社セクション ---- */
        .pi-info-section {
            display: flex;
            gap: 16px;
            margin-bottom: 14px;
            padding-bottom: 14px;
            border-bottom: 2px solid;
            border-image: linear-gradient(135deg, #e91e63, #7c3aed) 1;
        }
        .pi-customer { flex: 1; font-size: 12px; line-height: 2; }
        .pi-cust-name {
            font-size: 20px; font-weight: 900; color: #111;
            border-bottom: 2px solid #e91e63;
            display: inline-block;
            padding-bottom: 2px;
            margin-bottom: 4px;
        }
        .pi-our-side {
            width: 260px;
            font-size: 11px;
            line-height: 1.9;
            color: #444;
        }
        .pi-our-name { font-size: 14px; font-weight: 900; color: #111; }
        .pi-our-reg {
            font-size: 10px; color: #e91e63; margin-top: 6px;
            display: inline-block;
            padding: 2px 8px;
            border-left: 3px solid #e91e63;
            background: rgba(233,30,99,0.05);
        }

        /* ---- 品目テーブル ---- */
        .pi-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
            border: 1px solid #e0d0f0;
        }
        .pi-table th {
            background: linear-gradient(135deg, #e91e63, #7c3aed);
            color: #fff;
            border: 1px solid rgba(255,255,255,0.15);
            padding: 7px 6px;
            text-align: center;
            font-weight: 700;
            font-size: 11px;
            white-space: nowrap;
        }
        .pi-table td {
            border: 1px solid #e0d0f0;
            padding: 4px 6px;
            vertical-align: middle;
        }
        .pi-table tbody tr:nth-child(even) td { background: rgba(233,30,99,0.03); }
        .pi-td-r { text-align: right; }
        .pi-td-c { text-align: center; }

        /* ---- フッター合計行 ---- */
        .pi-footer-row {
            display: flex;
            border: 1px solid #e0d0f0;
            border-top: none;
        }
        .pi-fc {
            flex: 1;
            padding: 8px 12px;
            border-right: 1px solid #e0d0f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            background: #f8f6ff;
        }
        .pi-fc:last-child {
            border-right: none;
            font-weight: 700;
            font-size: 13px;
            background: linear-gradient(135deg, #e91e63, #7c3aed);
        }
        .pi-fc-lbl { color: #666; }
        .pi-fc:last-child .pi-fc-lbl { color: rgba(255,255,255,0.85); }
        .pi-fc-val { font-weight: 700; }
        .pi-fc:last-child .pi-fc-val { color: #fff; font-size: 16px; }

        /* ---- 備考 ---- */
        .pi-note {
            margin-top: 12px;
            padding: 8px 12px;
            border: 1px solid #e0d0f0;
            border-left: 3px solid #e91e63;
            font-size: 11px;
            color: #444;
            line-height: 1.8;
            background: rgba(233,30,99,0.02);
        }
```

**Step 3: 確認**

`/* ---- 改ページ ---- */` の行（`.pi-page-break`）がまだ残っていることを確認。

---

### Task 3: `buildInvoiceHTML()` のHTML構造を更新

**Files:**
- Modify: `C:\Users\MYPC\Development\請求書\invoice.html` (line ~1578)

**Step 1: 関数内のHTMLを置き換え**

`return \`` から `\`;` までの全HTMLを以下に置き換える。

old_string（`return \`` の開始から `</div>\`;` まで）:
```js
        return `
        <div class="pi-page">
            <div class="pi-header-bar"></div>
            <div class="pi-head-row">
                <div class="pi-head-left">
                    <img src="${LOGO_B64}" style="width:54px;height:54px;object-fit:contain;border-radius:4px;" alt="logo">
                    <div class="pi-title-box">請　求　書</div>
                </div>
                <div class="pi-head-right">
                    <div class="pi-billing-month">${escHtml(billingLabel)}</div>
                    <div>PAGE &nbsp; 1 / 1</div>
                    <div>発行日&emsp;<strong>${escHtml(data.invDate)}</strong></div>
                    <div>No. &emsp;<strong>${escHtml(data.invoiceNumber)}</strong></div>
                </div>
            </div>

            <div class="pi-info-section">
                <div class="pi-customer">
                    ${data.clientAddress ? `<div style="font-size:11px;">${escHtml(data.clientAddress)}</div>` : ''}
                    <div class="pi-cust-name">${escHtml(data.clientName || '　')}</div>
                    <div style="font-size:13px; margin-top:2px;">様</div>
                    ${data.clientContact ? `<div style="font-size:11px;">TEL &nbsp;${escHtml(data.clientContact)}</div>` : ''}
                    ${data.regNumber ? `<div class="pi-reg-num">登録番号：${escHtml(data.regNumber)}</div>` : ''}
                </div>
                <div class="pi-our-side">
                    <div>〒532-0012</div>
                    <div>大阪市淀川区木川東4-3-34-514</div>
                    <div class="pi-our-name">株式会社さくらねっと</div>
                    <div>TEL 06-7777-2720&emsp;FAX 06-6303-3767</div>
                    <div>担当者：伏見</div>
                </div>
            </div>

            <table class="pi-table">
                <thead>
                    <tr>
                        <th style="width:42%;">商品コード／商品名</th>
                        <th style="width:8%;">数量</th>
                        <th style="width:8%;">単位</th>
                        <th style="width:16%;">単価</th>
                        <th style="width:16%;">金額</th>
                    </tr>
                </thead>
                <tbody>${rows}${blankRows}</tbody>
            </table>
            <div class="pi-footer-row">
                <div class="pi-fc"><span class="pi-fc-lbl">税抜額</span><span class="pi-fc-val">¥${formatNum(data.subtotal)}</span></div>
                <div class="pi-fc"><span class="pi-fc-lbl">消費税額</span><span class="pi-fc-val">¥${formatNum(data.tax)}</span></div>
                <div class="pi-fc"><span class="pi-fc-lbl">合　計</span><span class="pi-fc-val" style="font-size:16px; color:#111;">¥${formatNum(data.total)}</span></div>
            </div>
            ${data.note ? `<div class="pi-note"><strong>備考：</strong>${escHtml(data.note).replace(/\n/g,'<br>')}</div>` : ''}
        </div>`;
```

new_string:
```js
        return `
        <div class="pi-page">
            <div class="pi-header-bar"></div>
            <div class="pi-content">
                <div class="pi-head-row">
                    <div class="pi-head-left">
                        <img src="${LOGO_B64}" style="width:50px;height:50px;object-fit:contain;border-radius:6px;" alt="logo">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <div class="pi-title-accent"></div>
                            <div class="pi-title-box">請　求　書</div>
                        </div>
                    </div>
                    <div class="pi-head-right">
                        <div class="pi-billing-month">${escHtml(billingLabel)}</div>
                        <div>発行日&emsp;<strong>${escHtml(data.invDate)}</strong></div>
                        <div>No.&emsp;<strong>${escHtml(data.invoiceNumber)}</strong></div>
                    </div>
                </div>

                <div class="pi-info-section">
                    <div class="pi-customer">
                        ${data.clientAddress ? `<div style="font-size:11px;color:#666;">${escHtml(data.clientAddress)}</div>` : ''}
                        <div class="pi-cust-name">${escHtml(data.clientName || '　')}</div>
                        <div style="font-size:13px;margin-top:2px;">様</div>
                        ${data.clientContact ? `<div style="font-size:11px;color:#555;">TEL &nbsp;${escHtml(data.clientContact)}</div>` : ''}
                    </div>
                    <div class="pi-our-side">
                        <div>〒532-0012</div>
                        <div>大阪市淀川区木川東4-3-34-514</div>
                        <div class="pi-our-name">株式会社さくらねっと</div>
                        <div>TEL 06-7777-2720&emsp;FAX 06-6303-3767</div>
                        <div>担当者：伏見</div>
                        <div class="pi-our-reg">登録番号：${COMPANY_REG_NUMBER}</div>
                    </div>
                </div>

                <table class="pi-table">
                    <thead>
                        <tr>
                            <th style="width:42%;">商品コード／商品名</th>
                            <th style="width:8%;">数量</th>
                            <th style="width:8%;">単位</th>
                            <th style="width:16%;">単価</th>
                            <th style="width:16%;">金額</th>
                        </tr>
                    </thead>
                    <tbody>${rows}${blankRows}</tbody>
                </table>
                <div class="pi-footer-row">
                    <div class="pi-fc"><span class="pi-fc-lbl">税抜額</span><span class="pi-fc-val">¥${formatNum(data.subtotal)}</span></div>
                    <div class="pi-fc"><span class="pi-fc-lbl">消費税額</span><span class="pi-fc-val">¥${formatNum(data.tax)}</span></div>
                    <div class="pi-fc"><span class="pi-fc-lbl">合　計</span><span class="pi-fc-val">¥${formatNum(data.total)}</span></div>
                </div>
                ${data.note ? `<div class="pi-note"><strong>備考：</strong>${escHtml(data.note).replace(/\n/g,'<br>')}</div>` : ''}
            </div>
        </div>`;
```

**Step 2: 構文チェック**

```bash
cd "C:/Users/MYPC/Development/請求書"
node -e "
const fs = require('fs');
const html = fs.readFileSync('invoice.html','utf8');
const m = html.match(/<script>([\s\S]*?)<\/script>/g);
console.log('script blocks:', m ? m.length : 0);
" 2>&1
```

エラーが出ないことを確認。

**Step 3: まとめてコミット**

```bash
cd "C:/Users/MYPC/Development/請求書"
git add invoice.html
git commit -m "feat: PDFデザインをSAKURAグラデーションに刷新・登録番号T9120001205370追加"
```

---

## 動作確認チェックリスト

1. ブラウザで `invoice.html` を開く
2. 任意の請求書を選択 or 新規作成
3. 「🖨 PDF出力」ボタンをクリック
4. プレビューモーダルで確認:
   - [ ] トップバーがピンク→パープルのグラデーション
   - [ ] 「請　求　書」タイトルがグラデーション文字
   - [ ] テーブルヘッダーがグラデーション背景/白文字
   - [ ] 合計セルがグラデーション背景/白文字
   - [ ] 右側に「登録番号：T9120001205370」が表示される
   - [ ] 登録番号のないデータでも正常表示
