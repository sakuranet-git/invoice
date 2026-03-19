# 請求書PDF生成・メール添付・印鑑ドラッグ 実装プラン

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 請求書をA4プレビューで確認し、ドラッグ配置した印鑑込みのPDFをメール添付して送信できるようにする。

**Architecture:** `invoice.html` 単一ファイルへの変更と `invoice_send.php` のPDF添付対応。html2pdf.js CDNでブラウザ側PDF生成 → base64でPHPに送信 → MIME添付メール送信。

**Tech Stack:** Vanilla JS, html2pdf.js (CDN), PHP mb_send_mail (multipart/mixed), Firebase Firestore v8 (既存)

---

## 背景・重要な仕様

- `invoice.html` は `C:\Users\MYPC\Development\請求書\invoice.html`（約1697行 ※base64埋込で実際は巨大）
- `invoice_send.php` は同ディレクトリ
- Firestore `invoices` コレクション: `invDueDate` フィールドを廃止し `billingMonth`（例: `"2026-03"`）を追加
- 既存の印鑑base64定数: `STAMP_CO_B64`（会社印）、`STAMP_PER_B64`（個人印）、`LOGO_B64`（ロゴ）はJSに既に定義済み
- テスト環境なし（ブラウザで直接確認）
- 変更前に確認不要（直接実装OK）

---

## Task 1: 請求対象月フィールド追加・支払期限削除

**Files:**
- Modify: `請求書/invoice.html` (lines 731-738, 1062-1072, 1229-1248, 1287-1307, 1657)

**Step 1: フォームHTML変更（支払期限 → 請求対象月）**

`lines 731-738` の該当箇所（発行日・支払期限 2つの form-group）を以下に変更:

```html
                    <div class="form-group">
                        <label>発行日</label>
                        <input type="date" id="invDate">
                    </div>
                    <div class="form-group">
                        <label>請求対象月</label>
                        <div style="display:flex; gap:6px; align-items:center;">
                            <select id="billingYear" style="flex:1;"></select>
                            <span style="color:var(--text-muted);">年</span>
                            <select id="billingMonth" style="flex:1;"></select>
                            <span style="color:var(--text-muted);">月分</span>
                        </div>
                    </div>
```

**Step 2: setDefaultDates() 更新（line 1062-1072）**

```js
    function setDefaultDates() {
        const today = new Date();
        document.getElementById('invDate').value = formatDateInput(today);
        // 請求対象月デフォルト: 15日以前は前月、16日以降は当月
        const bm = today.getDate() <= 15
            ? new Date(today.getFullYear(), today.getMonth() - 1, 1)
            : today;
        initBillingMonthSelects(bm.getFullYear(), bm.getMonth() + 1);
    }

    function initBillingMonthSelects(year, month) {
        const yearSel  = document.getElementById('billingYear');
        const monthSel = document.getElementById('billingMonth');
        yearSel.innerHTML = '';
        const curY = new Date().getFullYear();
        for (let y = curY - 2; y <= curY + 1; y++) {
            yearSel.innerHTML += `<option value="${y}" ${y===year?'selected':''}>${y}</option>`;
        }
        monthSel.innerHTML = '';
        for (let m = 1; m <= 12; m++) {
            monthSel.innerHTML += `<option value="${m}" ${m===month?'selected':''}>${m}</option>`;
        }
    }

    function getBillingMonthValue() {
        const y = document.getElementById('billingYear').value;
        const m = String(document.getElementById('billingMonth').value).padStart(2,'0');
        return `${y}-${m}`;  // "2026-03"
    }

    function getBillingMonthLabel() {
        const y = document.getElementById('billingYear').value;
        const m = document.getElementById('billingMonth').value;
        return `${y}年${m}月分`;  // "2026年3月分"
    }
```

**Step 3: loadInvoice() 更新（line 1241付近）**

`invDueDate` の行を削除し `billingMonth` の読込を追加:

```js
// 削除: document.getElementById('invDueDate').value = data.invDueDate || '';
// 追加:
const bm = data.billingMonth || getBillingMonthValue();
const [by, bmm] = bm.split('-');
initBillingMonthSelects(parseInt(by), parseInt(bmm));
```

**Step 4: collectFormData() 更新（line 1295付近）**

```js
// 削除: invDueDate: document.getElementById('invDueDate').value,
// 追加:
billingMonth: getBillingMonthValue(),
```

**Step 5: clearForm の ID配列更新（line 1657付近）**

```js
['invNumber','invDate','clientName','clientContact','clientEmail','clientAddress','invNote']
// 'invDueDate' を削除
```

**Step 6: git commit**

```bash
cd "C:\Users\MYPC\Development\請求書"
git add invoice.html
git commit -m "feat: 請求対象月フィールド追加・支払期限削除"
```

---

## Task 2: html2pdf.js CDN追加 + プレビューモーダルHTML追加

**Files:**
- Modify: `請求書/invoice.html`

**Step 1: html2pdf.js CDN を Firebase scriptsの直前に追加**

`<script src="https://www.gstatic.com/firebasejs/` で始まる行の直前に:

```html
<!-- html2pdf.js: ブラウザでA4 PDF生成 -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
```

**Step 2: プレビューモーダルHTMLを `<div id="printArea"></div>` の直後に追加**

```html
<!-- ===== A4プレビュー + 印鑑ドラッグ モーダル ===== -->
<div id="previewModal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.8); z-index:9000; overflow-y:auto; padding:20px 0;">
    <div style="max-width:860px; margin:0 auto;">
        <!-- ヘッダーバー -->
        <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 16px; background:#1a1525; border-radius:8px 8px 0 0; border:1px solid var(--glass-border);">
            <span style="font-size:14px; font-weight:700; color:#e2d9f3;">🖨 A4プレビュー &nbsp;<span style="font-size:11px; color:#a78bfa; font-weight:400;">印鑑をドラッグして配置できます</span></span>
            <div style="display:flex; gap:8px;">
                <button class="btn btn-ghost" onclick="closePreviewModal()" style="font-size:12px; padding:4px 14px;">✕ 閉じる</button>
                <button class="btn btn-ghost" onclick="window.print()" style="font-size:12px; padding:4px 14px;">🖨 印刷/PDF保存</button>
                <button class="btn btn-success" onclick="openMailFromPreview()" style="font-size:12px; padding:4px 14px;">📧 このPDFで送信</button>
            </div>
        </div>
        <!-- A4キャンバス -->
        <div id="a4Canvas" style="width:794px; min-height:1123px; background:#fff; margin:0 auto; position:relative; box-shadow:0 4px 24px rgba(0,0,0,0.5);">
            <div id="a4Content"></div>
            <!-- 会社印（ドラッグ可能） -->
            <img id="stampCo" src="" alt="社印"
                style="position:absolute; width:64px; height:64px; object-fit:contain; cursor:grab; user-select:none; opacity:0.9;"
                onmousedown="startStampDrag(event,'stampCo')">
            <!-- 個人印（ドラッグ可能） -->
            <img id="stampPer" src="" alt="個人印"
                style="position:absolute; width:52px; height:52px; object-fit:contain; cursor:grab; user-select:none; opacity:0.9;"
                onmousedown="startStampDrag(event,'stampPer')">
        </div>
    </div>
</div>
```

**Step 3: メール確認モーダルHTMLを追加（プレビューモーダルの直後）**

```html
<!-- ===== メール確認モーダル（PDF添付用） ===== -->
<div id="mailConfirmModal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.7); z-index:9500; display:none; align-items:center; justify-content:center;">
    <div style="background:#1e1b3a; border:1px solid var(--glass-border); border-radius:12px; padding:28px; width:500px; max-width:95vw;">
        <div style="font-size:16px; font-weight:700; margin-bottom:20px; color:#e2d9f3;">✉ メール送信（PDF添付）</div>
        <div style="margin-bottom:12px;">
            <label style="font-size:11px; color:var(--text-muted); display:block; margin-bottom:4px;">宛先</label>
            <input type="email" id="mailTo2" style="width:100%; box-sizing:border-box;" placeholder="example@company.co.jp">
        </div>
        <div style="margin-bottom:12px;">
            <label style="font-size:11px; color:var(--text-muted); display:block; margin-bottom:4px;">件名</label>
            <input type="text" id="mailSubject2" style="width:100%; box-sizing:border-box;">
        </div>
        <div style="margin-bottom:12px;">
            <label style="font-size:11px; color:var(--text-muted); display:block; margin-bottom:4px;">本文</label>
            <textarea id="mailBody2" style="width:100%; box-sizing:border-box; min-height:140px;"></textarea>
        </div>
        <div id="mailStatus2" style="font-size:13px; color:var(--warning); min-height:20px; margin-bottom:8px;"></div>
        <div style="display:flex; justify-content:flex-end; gap:8px;">
            <button class="btn btn-ghost" onclick="closeMailConfirmModal()">キャンセル</button>
            <button class="btn btn-success" onclick="sendMailWithPdf()">📤 送信する</button>
        </div>
    </div>
</div>
```

**Step 4: git commit**

```bash
git add invoice.html
git commit -m "feat: html2pdf.js CDN追加・プレビューモーダル・メール確認モーダルHTML追加"
```

---

## Task 3: A4 CSS修正（プレビュー + 印刷兼用）

**Files:**
- Modify: `請求書/invoice.html` (lines 423-597 の印刷CSS付近)

**Step 1: `#printArea` と `@media print` のCSS修正**

既存の `#printArea { display: none; ... }` と `@media print` ブロックを以下に変更:

```css
        /* ===== A4プレビュー + PDF印刷専用スタイル ===== */
        @media print {
            body > *:not(#printArea) { display: none !important; }
            #printArea {
                display: block !important;
                position: fixed;
                inset: 0;
                z-index: 99999;
                background: #fff;
            }
        }

        #printArea {
            display: none;
        }

        /* A4キャンバス共通スタイル（プレビュー・PDF生成・印刷で共用） */
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
            padding: 57px 76px 57px 76px; /* 15mm上下, 20mm左右 = 57px, 76px */
        }

        /* ---- 上部ライン ---- */
        .pi-header-bar {
            background: #111;
            height: 5px;
            width: 100%;
            margin-bottom: 16px;
        }

        /* ---- ページ最上部：タイトル行 ---- */
        .pi-head-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }
        .pi-head-left { display: flex; align-items: center; gap: 12px; }
        .pi-title-box {
            font-size: 22px; font-weight: 900; letter-spacing: 8px;
            color: #111;
            border: 2.5px solid #111;
            padding: 5px 22px;
        }
        .pi-head-right { text-align: right; font-size: 11px; color: #333; line-height: 2.1; }
        .pi-billing-month { font-size: 13px; font-weight: 700; color: #111; }

        /* ---- 顧客 / 自社セクション ---- */
        .pi-info-section {
            display: flex;
            gap: 16px;
            margin-bottom: 12px;
            border-bottom: 2px solid #111;
            padding-bottom: 12px;
        }
        .pi-customer { flex: 1; font-size: 12px; line-height: 2; }
        .pi-cust-name {
            font-size: 19px; font-weight: 900; color: #111;
            border-bottom: 2px solid #111;
            display: inline-block;
            padding-bottom: 2px;
            margin-bottom: 4px;
        }
        .pi-reg-num {
            font-size: 11px; color: #555; margin-top: 6px;
            display: inline-block;
            padding: 2px 7px;
            border-left: 3px solid #555;
        }
        .pi-our-side {
            width: 260px;
            font-size: 11px;
            line-height: 2;
            color: #333;
        }
        .pi-our-name { font-size: 14px; font-weight: 900; color: #111; }

        /* ---- 品目テーブル ---- */
        .pi-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
            border: 1.5px solid #333;
        }
        .pi-table th {
            background: #e8e8e8;
            color: #111;
            border: 1px solid #333;
            padding: 6px;
            text-align: center;
            font-weight: 700;
            font-size: 11px;
            white-space: nowrap;
        }
        .pi-table td {
            border: 1px solid #bbb;
            padding: 4px 6px;
            vertical-align: middle;
        }
        .pi-td-r { text-align: right; }
        .pi-td-c { text-align: center; }

        /* ---- フッター合計行 ---- */
        .pi-footer-row {
            display: flex;
            border: 1.5px solid #333;
            border-top: none;
        }
        .pi-fc {
            flex: 1;
            padding: 6px 10px;
            border-right: 1px solid #999;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
        }
        .pi-fc:last-child {
            border-right: none;
            font-weight: 700;
            font-size: 13px;
            background: #f0f0f0;
        }
        .pi-fc-lbl { color: #555; }
        .pi-fc-val { font-weight: 700; }

        /* ---- 備考 ---- */
        .pi-note {
            margin-top: 12px;
            padding: 8px 12px;
            border: 1px solid #bbb;
            border-left: 3px solid #555;
            font-size: 11px;
            color: #444;
            line-height: 1.8;
        }

        /* ---- 改ページ ---- */
        .pi-page-break { page-break-before: always; }
        .pi-table tr { page-break-inside: avoid; }
```

**Step 2: git commit**

```bash
git add invoice.html
git commit -m "feat: A4対応CSS（プレビュー・PDF・印刷兼用）"
```

---

## Task 4: printInvoice() リファクタ + 請求対象月表示

**Files:**
- Modify: `請求書/invoice.html` (lines 1461-1580)

**Step 1: printInvoice() を以下に書き換え**

```js
    // ─────────────────────────────────────────
    // 請求書HTML生成
    // ─────────────────────────────────────────
    function buildInvoiceHTML(data) {
        const billingLabel = getBillingMonthLabel();  // "2026年3月分"
        const rows = data.items.map(it => `
            <tr>
                <td>${escHtml(it.name)}</td>
                <td class="pi-td-r">${it.qty}</td>
                <td class="pi-td-c">${escHtml(it.unit)}</td>
                <td class="pi-td-r">¥${formatNum(it.price)}</td>
                <td class="pi-td-r">¥${formatNum(it.qty * it.price)}</td>
            </tr>`).join('');

        // 空行を埋めて最低20行表示
        const emptyRows = Math.max(0, 20 - data.items.length);
        const blankRows = Array(emptyRows).fill('<tr><td>&nbsp;</td><td></td><td></td><td></td><td></td></tr>').join('');

        return `
        <div class="pi-page" id="piPage">
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
    }

    function printInvoice() {
        const data = collectFormData();
        // 印刷用: printAreaにセットして window.print()
        const printArea = document.getElementById('printArea');
        printArea.innerHTML = buildInvoiceHTML(data);
        window.print();
    }

    function openPreviewModal() {
        const data = collectFormData();
        // A4キャンバスにHTMLをセット
        document.getElementById('a4Content').innerHTML = buildInvoiceHTML(data);
        // 印鑑画像をセット
        document.getElementById('stampCo').src  = STAMP_CO_B64;
        document.getElementById('stampPer').src = STAMP_PER_B64;
        // 印鑑位置をlocalStorageから復元（なければデフォルト）
        const coPos  = JSON.parse(localStorage.getItem('stampCoPos')  || 'null') || { x: 490, y: 140 };
        const perPos = JSON.parse(localStorage.getItem('stampPerPos') || 'null') || { x: 490, y: 195 };
        const co  = document.getElementById('stampCo');
        const per = document.getElementById('stampPer');
        co.style.left  = coPos.x  + 'px';
        co.style.top   = coPos.y  + 'px';
        per.style.left = perPos.x + 'px';
        per.style.top  = perPos.y + 'px';
        document.getElementById('previewModal').style.display = 'block';
    }

    function closePreviewModal() {
        document.getElementById('previewModal').style.display = 'none';
    }
```

**Step 2: ツールバーの「🖨 PDF出力」ボタンを `openPreviewModal()` 呼び出しに変更（line 707付近）**

```html
<!-- 変更前 -->
<button class="btn btn-ghost" onclick="printInvoice()">🖨 PDF出力</button>
<!-- 変更後 -->
<button class="btn btn-ghost" onclick="openPreviewModal()">🖨 PDF出力</button>
```

**Step 3: git commit**

```bash
git add invoice.html
git commit -m "feat: buildInvoiceHTML()リファクタ・請求対象月表示・プレビューモーダル表示"
```

---

## Task 5: 印鑑ドラッグ機能 + localStorage保存

**Files:**
- Modify: `請求書/invoice.html` (JS末尾付近、`sendMail()` の後に追加)

**Step 1: ドラッグ関数を追加**

```js
    // ─────────────────────────────────────────
    // 印鑑ドラッグ機能
    // ─────────────────────────────────────────
    function startStampDrag(e, stampId) {
        e.preventDefault();
        const el = document.getElementById(stampId);
        const canvas = document.getElementById('a4Canvas');
        const rect = canvas.getBoundingClientRect();
        const startX = e.clientX - el.offsetLeft;
        const startY = e.clientY - el.offsetTop;

        el.style.cursor = 'grabbing';

        function onMove(ev) {
            let x = ev.clientX - startX;
            let y = ev.clientY - startY;
            // a4Canvas内に制限
            x = Math.max(0, Math.min(x, 794 - el.offsetWidth));
            y = Math.max(0, Math.min(y, canvas.offsetHeight - el.offsetHeight));
            el.style.left = x + 'px';
            el.style.top  = y + 'px';
        }

        function onUp() {
            el.style.cursor = 'grab';
            document.removeEventListener('mousemove', onMove);
            document.removeEventListener('mouseup', onUp);
            // 位置をlocalStorageに保存
            const storageKey = stampId === 'stampCo' ? 'stampCoPos' : 'stampPerPos';
            localStorage.setItem(storageKey, JSON.stringify({
                x: parseInt(el.style.left),
                y: parseInt(el.style.top)
            }));
        }

        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
    }
```

**Step 2: ブラウザで動作確認**

1. `C:\Users\MYPC\Development\請求書\invoice.html` をブラウザで開く
2. 請求書フォームに顧客情報を入力
3. 「🖨 PDF出力」クリック → A4プレビューモーダルが開く
4. 印鑑（社印・個人印）をドラッグして好きな位置に移動できることを確認
5. モーダルを閉じて再度開くとlocalStorageから位置が復元されることを確認

**Step 3: git commit**

```bash
git add invoice.html
git commit -m "feat: 印鑑ドラッグ機能・localStorage位置保存"
```

---

## Task 6: PDF生成関数（html2pdf.js）

**Files:**
- Modify: `請求書/invoice.html` (印鑑ドラッグ関数の直後に追加)

**Step 1: PDF生成関数を追加**

```js
    // ─────────────────────────────────────────
    // PDF生成（html2pdf.js）
    // ─────────────────────────────────────────
    async function generatePdfBase64() {
        const data = collectFormData();
        const bm = getBillingMonthValue().replace('-','');  // "202603"
        const filename = `請求書_${bm}_${data.invoiceNumber}.pdf`;

        // a4Canvasをターゲットにする（印鑑の絶対配置を含む）
        const element = document.getElementById('a4Canvas');

        const opt = {
            margin:      [0, 0, 0, 0],
            filename:    filename,
            image:       { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, useCORS: true, backgroundColor: '#fff' },
            jsPDF:       { unit: 'px', format: [794, 1123], orientation: 'portrait' }
        };

        // base64文字列として取得
        const pdf = await html2pdf().set(opt).from(element).outputPdf('datauristring');
        // "data:application/pdf;base64,XXXX..." → "XXXX..." 部分だけ
        return { base64: pdf.split(',')[1], filename };
    }
```

**Step 2: git commit**

```bash
git add invoice.html
git commit -m "feat: html2pdf.js でPDF base64生成関数追加"
```

---

## Task 7: メール送信フロー変更（プレビュー → PDF → 送信）

**Files:**
- Modify: `請求書/invoice.html` (openMailModal, sendMail 付近)

**Step 1: 既存の `openMailModal()` を変更**

既存の `openMailModal()` は既存の `#mailModal` を使っていたが、新フローでは「プレビューモーダルを開く」に変更する:

```js
    function openMailModal() {
        openPreviewModal();  // まずプレビューを開く
    }
```

**Step 2: `openMailFromPreview()` 関数を追加**

プレビューの「📧 このPDFで送信」ボタン用:

```js
    function openMailFromPreview() {
        const data = collectFormData();
        const bm = getBillingMonthLabel();  // "2026年3月分"
        const month = new Date(data.invDate || Date.now()).getMonth() + 1;
        const clientName = data.clientName || 'お客様';

        document.getElementById('mailTo2').value      = data.clientEmail || '';
        document.getElementById('mailSubject2').value = `【さくらねっと】${bm} 請求書のご案内（${data.invoiceNumber}）`;
        document.getElementById('mailBody2').value    =
`${clientName} 御中

いつも大変お世話になっております。
株式会社さくらねっとでございます。

${bm}分の請求書をPDFにてお送りいたします。
ご確認のほどよろしくお願いいたします。

【請求書番号】${data.invoiceNumber}
【発行日】${data.invDate}
【請求対象】${bm}
【ご請求金額（税込）】¥${formatNum(data.total)}

ご不明な点がございましたら、お気軽にお問い合わせください。

─────────────────────────────
株式会社さくらねっと
TEL: 06-7777-2720 / FAX: 06-6303-3767
E-mail: system@sakuranet-co.jp
─────────────────────────────`;

        document.getElementById('mailStatus2').textContent = '';
        document.getElementById('mailConfirmModal').style.display = 'flex';
    }

    function closeMailConfirmModal() {
        document.getElementById('mailConfirmModal').style.display = 'none';
    }
```

**Step 3: `sendMailWithPdf()` 関数を追加**

```js
    async function sendMailWithPdf() {
        const to      = document.getElementById('mailTo2').value.trim();
        const subject = document.getElementById('mailSubject2').value.trim();
        const body    = document.getElementById('mailBody2').value.trim();
        const status  = document.getElementById('mailStatus2');

        if (!to)      { status.textContent = '⚠ 宛先メールアドレスを入力してください'; return; }
        if (!subject) { status.textContent = '⚠ 件名を入力してください'; return; }

        status.textContent = '📄 PDF生成中...';

        try {
            const { base64, filename } = await generatePdfBase64();

            status.textContent = '📤 送信中...';

            const res = await fetch('invoice_send.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ to, subject, body, pdf_base64: base64, pdf_filename: filename }),
            });
            const json = await res.json();

            if (json.success) {
                showToast('✅ メールを送信しました（PDF添付）');
                closeMailConfirmModal();
                closePreviewModal();
            } else {
                status.textContent = '❌ ' + (json.error || '送信失敗');
            }
        } catch (e) {
            status.textContent = '❌ エラー: ' + e.message;
        }
    }
```

**Step 4: ブラウザで確認**

1. プレビューモーダルで印鑑を配置
2. 「📧 このPDFで送信」クリック → メール確認モーダルが開く
3. 宛先・件名・本文が自動入力されることを確認
4. （実際の送信はTask 8のPHP対応後に確認）

**Step 5: git commit**

```bash
git add invoice.html
git commit -m "feat: メール送信フロー変更（プレビュー→PDF生成→送信）"
```

---

## Task 8: invoice_send.php PDF添付対応

**Files:**
- Modify: `請求書/invoice_send.php`

**Step 1: invoice_send.php をPDF添付対応版に書き換え**

```php
<?php
/**
 * invoice_send.php
 * SAKURA 請求書システム — メール送信エンドポイント（PDF添付対応）
 *
 * リクエスト: POST (JSON)
 *   {
 *     "to": "xxx@example.com",
 *     "subject": "件名",
 *     "body": "本文",
 *     "pdf_base64": "JVBERi...",   // base64エンコードされたPDF（省略可）
 *     "pdf_filename": "請求書_202603_001.pdf"  // 添付ファイル名（省略可）
 *   }
 */

declare(strict_types=1);

header('Content-Type: application/json; charset=UTF-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

const FROM_EMAIL = 'system@sakuranet-co.jp';
const FROM_NAME  = '株式会社さくらねっと';
const BCC_EMAIL  = 'system@sakuranet-co.jp';

$input = file_get_contents('php://input');
$data  = json_decode($input, true);

if (json_last_error() !== JSON_ERROR_NONE || !is_array($data)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => '不正なリクエスト形式です']);
    exit;
}

$to          = trim($data['to']          ?? '');
$subject     = trim($data['subject']     ?? '');
$body        = trim($data['body']        ?? '');
$pdfBase64   = trim($data['pdf_base64']  ?? '');
$pdfFilename = trim($data['pdf_filename'] ?? '請求書.pdf');

$errors = [];
if (empty($to) || !filter_var($to, FILTER_VALIDATE_EMAIL)) { $errors[] = '宛先メールアドレスが不正です'; }
if (empty($subject)) { $errors[] = '件名が入力されていません'; }
if (empty($body))    { $errors[] = '本文が入力されていません'; }

if ($errors) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => implode(' / ', $errors)]);
    exit;
}

try {
    $result = sendMailWithAttachment($to, $subject, $body, $pdfBase64, $pdfFilename);
    echo json_encode($result);
} catch (Throwable $e) {
    error_log('[invoice_send] 予期しないエラー: ' . $e->getMessage());
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'サーバーエラーが発生しました']);
}

function sendMailWithAttachment(
    string $to,
    string $subject,
    string $body,
    string $pdfBase64,
    string $pdfFilename
): array {
    mb_language('Japanese');
    mb_internal_encoding('UTF-8');

    $boundary = '----=_Part_' . md5(uniqid((string)mt_rand(), true));

    if (empty($pdfBase64)) {
        // PDF添付なし: プレーンテキストメール
        $headers  = "From: " . mb_encode_mimeheader(FROM_NAME) . " <" . FROM_EMAIL . ">\r\n";
        $headers .= "Bcc: " . BCC_EMAIL . "\r\n";
        $headers .= "MIME-Version: 1.0\r\n";
        $headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
        $headers .= "Content-Transfer-Encoding: base64\r\n";

        $success = mb_send_mail($to, $subject, $body, $headers);
    } else {
        // PDF添付あり: multipart/mixed
        $headers  = "From: " . mb_encode_mimeheader(FROM_NAME) . " <" . FROM_EMAIL . ">\r\n";
        $headers .= "Bcc: " . BCC_EMAIL . "\r\n";
        $headers .= "MIME-Version: 1.0\r\n";
        $headers .= "Content-Type: multipart/mixed; boundary=\"{$boundary}\"\r\n";

        // 本文パート
        $encodedBody = base64_encode($body);
        $bodyChunked = chunk_split($encodedBody, 76, "\r\n");

        // PDFパート
        $pdfChunked  = chunk_split($pdfBase64, 76, "\r\n");
        $encodedFilename = mb_encode_mimeheader($pdfFilename, 'UTF-8', 'B');

        $messageBody  = "--{$boundary}\r\n";
        $messageBody .= "Content-Type: text/plain; charset=UTF-8\r\n";
        $messageBody .= "Content-Transfer-Encoding: base64\r\n\r\n";
        $messageBody .= $bodyChunked . "\r\n";

        $messageBody .= "--{$boundary}\r\n";
        $messageBody .= "Content-Type: application/pdf; name=\"{$encodedFilename}\"\r\n";
        $messageBody .= "Content-Transfer-Encoding: base64\r\n";
        $messageBody .= "Content-Disposition: attachment; filename=\"{$encodedFilename}\"\r\n\r\n";
        $messageBody .= $pdfChunked . "\r\n";

        $messageBody .= "--{$boundary}--\r\n";

        $success = mb_send_mail($to, $subject, $messageBody, $headers);
    }

    if ($success) {
        error_log('[invoice_send] 送信成功: to=' . $to . ' pdf=' . ($pdfBase64 ? 'yes' : 'no'));
        return ['success' => true];
    }

    error_log('[invoice_send] mb_send_mail 失敗: to=' . $to);
    return ['success' => false, 'error' => 'メール送信に失敗しました。サーバーのメール設定を確認してください。'];
}
```

**Step 2: git commit**

```bash
git add invoice_send.php
git commit -m "feat: invoice_send.php PDF添付（multipart/mixed MIME）対応"
```

---

## Task 9: 動作確認 & WinSCPアップロード

**Step 1: ローカルで総合確認**

確認項目:
- [ ] 請求書フォームに「請求対象月」ドロップダウンが表示される
- [ ] 「支払期限」フィールドが消えている
- [ ] 「🖨 PDF出力」クリック → A4プレビューモーダルが開く
- [ ] 請求対象月がヘッダー右上に表示される（例：「2026年3月分」）
- [ ] 社印・個人印がドラッグで自由に移動できる
- [ ] モーダルを閉じて再度開いても印鑑位置が保持される
- [ ] 「🖨 印刷/PDF保存」クリック → ブラウザ印刷ダイアログが開く
- [ ] 「📧 このPDFで送信」クリック → メール確認モーダルが開く
- [ ] 「✉ メール送信」ボタンクリックも同じプレビューモーダルが開く
- [ ] A4サイズ、品目20行、罫線が正しく表示される

**Step 2: WinSCPアップロード**

```
ローカル: C:\Users\MYPC\Development\請求書\invoice.html
サーバー: /system/invoice/invoice.html

ローカル: C:\Users\MYPC\Development\請求書\invoice_send.php
サーバー: /system/invoice/invoice_send.php
```

**Step 3: git push**

```bash
cd "C:\Users\MYPC\Development\請求書"
git push origin main
```

**Step 4: RELEASE_NOTES.md に追記**

```markdown
## v（次バージョン） (2026-03-19)
- 請求対象月フィールド追加（支払期限を廃止）
- A4プレビューモーダル追加
- 電子印鑑ドラッグ配置機能（位置をlocalStorageに保存）
- html2pdf.js によるブラウザPDF生成
- メール送信にPDF添付（multipart/MIME）
- A4レイアウト改善・多品目時の自動改ページ対応
```
