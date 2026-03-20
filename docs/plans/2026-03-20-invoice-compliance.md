# インボイス制度・電子帳簿保存法 完全対応 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** `invoice.html` をインボイス制度（適格請求書）と電子帳簿保存法（真実性・可視性・検索要件）に完全対応させる。

**Architecture:** すべての変更は `invoice.html` 1ファイル（CSS・JS・HTML）のみ。Firebase Firestore の `invoices` コレクションに `locked`/`lockedAt`/`deleted`/`deletedAt` フィールドを追加。新コレクション `audit_log` に操作履歴を保存。税率は10%固定のまま（軽減税率なし）。

**Tech Stack:** Vanilla JS / HTML5 / CSS3, Firebase Firestore V8

---

### Task 1: インボイス制度 — PDF税表示の適正化

**Files:**
- Modify: `invoice.html:1868-1870`（PDFフッター税表示）
- Modify: `invoice.html:1866`（テーブル下の注記追加）

**Step 1: 変更を適用（PDFフッター）**

`invoice.html:1868-1870` の以下の箇所を：

```html
<div class="pi-fc"><span class="pi-fc-lbl">税抜額</span><span class="pi-fc-val">¥${formatNum(data.subtotal)}</span></div>
<div class="pi-fc"><span class="pi-fc-lbl">消費税額</span><span class="pi-fc-val">¥${formatNum(data.tax)}</span></div>
<div class="pi-fc"><span class="pi-fc-lbl">合　計</span><span class="pi-fc-val">¥${formatNum(data.total)}</span></div>
```

以下に置き換える：

```html
<div class="pi-fc"><span class="pi-fc-lbl">10%対象税抜額</span><span class="pi-fc-val">¥${formatNum(data.subtotal)}</span></div>
<div class="pi-fc"><span class="pi-fc-lbl">消費税(10%)</span><span class="pi-fc-val">¥${formatNum(data.tax)}</span></div>
<div class="pi-fc"><span class="pi-fc-lbl">合　計</span><span class="pi-fc-val">¥${formatNum(data.total)}</span></div>
```

**Step 2: 変更を適用（税率注記）**

`invoice.html:1871`（`${data.note ? ...}` の行）の直前に以下を追加：

```html
<div style="font-size:10px;color:#888;margin-top:4px;text-align:right;">※ 消費税率 10% 適用 ／ 適格請求書発行事業者登録番号：${COMPANY_REG_NUMBER}</div>
```

**Step 3: 目視確認**

プレビューモーダルを開き、フッターが「10%対象税抜額 / 消費税(10%) / 合計」になっており、テーブル下に登録番号注記が表示されることを確認。

**Step 4: Commit**

```bash
git add invoice.html
git commit -m "feat(invoice): インボイス制度対応 — PDF税率表示・登録番号注記"
```

---

### Task 2: 電子帳簿保存法 — 確定ロック機能

**Files:**
- Modify: `invoice.html:178-181`（CSS ステータスバッジ）
- Modify: `invoice.html:822-827`（select#invStatus）
- Modify: `invoice.html:1388-1393`（statusMap）
- Modify: `invoice.html:799-807`（ツールバー）
- Modify: `invoice.html:1576`（saveInvoice — 確定済みガード）
- Modify: `invoice.html:1602`（deleteInvoice — 確定済みガード）
- Modify: `invoice.html:1544`（loadInvoice — ロック状態UI反映）
- Add: `confirmInvoice()` 関数（`saveInvoice` の直後に追加）

**Step 1: CSS追加（確定バッジ）**

`invoice.html:181`（`.status-unpaid` 行）の直後に追加：

```css
.status-confirmed { background: rgba(233,30,99,0.2); color: #e91e63; font-weight:700; }
```

**Step 2: select に confirmed option 追加**

`invoice.html:822-827` の `<select id="invStatus">` を以下に置き換える：

```html
<select id="invStatus">
    <option value="draft">下書き</option>
    <option value="sent">送信済み</option>
    <option value="paid">入金済み</option>
    <option value="unpaid">未入金</option>
    <option value="confirmed" style="color:#e91e63;">🔒 確定（編集不可）</option>
</select>
```

**Step 3: statusMap に confirmed 追加**

`invoice.html:1388-1393` の `statusMap` を以下に置き換える：

```js
const statusMap = {
    draft:     { label: '下書き',       cls: 'status-draft'     },
    sent:      { label: '送信済み',      cls: 'status-sent'      },
    paid:      { label: '入金済み',      cls: 'status-paid'      },
    unpaid:    { label: '未入金',        cls: 'status-unpaid'    },
    confirmed: { label: '🔒 確定',       cls: 'status-confirmed' },
};
```

**Step 4: ツールバーに「確定」ボタン追加**

`invoice.html:803`（`<button ... onclick="saveInvoice()">💾 保存</button>` の直後）に追加：

```html
<button class="btn btn-ghost" id="confirmBtn" onclick="confirmInvoice()" style="color:#e91e63;border-color:rgba(233,30,99,0.4);" title="確定すると編集・削除できなくなります">🔒 確定</button>
```

**Step 5: confirmInvoice() 関数を追加**

`saveInvoice()` 関数の閉じ括弧（`}` line ~1597）の直後に追加：

```js
// ─────────────────────────────────────────
// 請求書確定（電子帳簿保存法：真実性確保）
// ─────────────────────────────────────────
async function confirmInvoice() {
    if (!currentInvoice || !currentInvoice.id) {
        showToast('⚠ 先に保存してから確定してください');
        return;
    }
    if (currentInvoice.locked) {
        showToast('この請求書はすでに確定済みです');
        return;
    }
    if (!confirm('請求書を確定しますか？\n確定後は編集・削除できなくなります（電子帳簿保存法）。')) return;

    try {
        await db.collection('invoices').doc(currentInvoice.id).update({
            status:    'confirmed',
            locked:    true,
            lockedAt:  firebase.firestore.FieldValue.serverTimestamp(),
        });
        await db.collection('audit_log').add({
            invoiceId:     currentInvoice.id,
            invoiceNumber: currentInvoice.invoiceNumber || '',
            action:        'confirm',
            clientName:    currentInvoice.clientName || '',
            total:         currentInvoice.total || 0,
            timestamp:     firebase.firestore.FieldValue.serverTimestamp(),
        });
        currentInvoice.locked = true;
        currentInvoice.status = 'confirmed';
        applyLockUI(true);
        showToast('🔒 確定しました（電子帳簿保存法対応）');
    } catch (e) {
        console.error('確定エラー:', e);
        showToast('❌ 確定に失敗しました: ' + e.message);
    }
}

function applyLockUI(locked) {
    const fields = ['invStatus','invDate','clientName','clientContact','clientEmail','clientAddress','paymentMethod','invNote'];
    fields.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.disabled = locked;
    });
    document.querySelectorAll('#itemsBody input').forEach(el => el.disabled = locked);
    document.querySelectorAll('#itemsBody button').forEach(el => el.disabled = locked);
    const addBtn = document.getElementById('addItemBtn');
    if (addBtn) addBtn.disabled = locked;
    document.getElementById('confirmBtn').style.display = locked ? 'none' : '';
    // 保存ボタンのテキスト変更
    const saveBtn = document.querySelector('[onclick="saveInvoice()"]');
    if (saveBtn) saveBtn.disabled = locked;
}
```

**Step 6: loadInvoice でロック状態を反映**

`invoice.html:1563`（`updateTotals()` 呼び出しの直後）に追加：

```js
applyLockUI(!!(data.locked));
```

**Step 7: saveInvoice にガード追加**

`invoice.html:1579`（`if (!data.clientName)` の直前）に追加：

```js
if (currentInvoice && currentInvoice.locked) { showToast('🔒 確定済みの請求書は編集できません'); return; }
```

**Step 8: deleteInvoice にガード追加**

`invoice.html:1604`（`if (!confirm...)` の直前）に追加：

```js
if (currentInvoice && currentInvoice.id === id && currentInvoice.locked) {
    showToast('🔒 確定済みの請求書は削除できません');
    return;
}
```

**Step 9: 目視確認**

1. 請求書を保存 → 「🔒 確定」ボタンを押す → 確認ダイアログ
2. 確定後：フォームがグレーアウト（disabled）、保存ボタン・確定ボタンが無効
3. 確定済み請求書を開いても編集できない

**Step 10: Commit**

```bash
git add invoice.html
git commit -m "feat(compliance): 電子帳簿保存法 — 確定ロック機能・audit_log追加"
```

---

### Task 3: 電子帳簿保存法 — 論理削除

**Files:**
- Modify: `invoice.html:1602-1615`（deleteInvoice）
- Modify: `invoice.html:1101`（subscribeInvoices — キャッシュフィルタ）

**Step 1: deleteInvoice を論理削除に変更**

`invoice.html:1602-1615` の `deleteInvoice` 関数全体を以下に置き換える：

```js
async function deleteInvoice(id, event) {
    event.stopPropagation();
    // 確定済みチェック
    const target = invoiceCache.find(inv => inv.id === id);
    if (target && target.locked) {
        showToast('🔒 確定済みの請求書は削除できません（電子帳簿保存法）');
        return;
    }
    if (!confirm('この請求書を削除しますか？\n（データはアーカイブとして保存されます）')) return;
    try {
        // 論理削除：Firestoreのドキュメントは残し、deletedフラグを立てる
        await db.collection('invoices').doc(id).update({
            deleted:   true,
            deletedAt: firebase.firestore.FieldValue.serverTimestamp(),
        });
        await db.collection('audit_log').add({
            invoiceId:     id,
            invoiceNumber: target ? target.invoiceNumber : '',
            action:        'delete',
            clientName:    target ? target.clientName : '',
            total:         target ? target.total : 0,
            timestamp:     firebase.firestore.FieldValue.serverTimestamp(),
        });
        if (currentInvoice && currentInvoice.id === id) { newInvoice(); }
        showToast('🗑 削除しました（アーカイブ保存済み）');
    } catch (e) {
        console.error('削除エラー:', e);
        showToast('❌ 削除に失敗しました: ' + e.message);
    }
}
```

**Step 2: subscribeInvoices でdeletedをフィルタ**

`invoice.html:1101` の以下の行を：

```js
invoiceCache = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
```

以下に置き換える：

```js
invoiceCache = snapshot.docs
    .map(doc => ({ id: doc.id, ...doc.data() }))
    .filter(inv => !inv.deleted);
```

**Step 3: 目視確認**

1. 下書き請求書を削除 → サイドバーから消える
2. Firestore コンソールで該当ドキュメントを確認 → `deleted: true` が付いている（消えていない）
3. 確定済み請求書の削除ボタンを押す → トーストでブロックされる

**Step 4: Commit**

```bash
git add invoice.html
git commit -m "feat(compliance): 電子帳簿保存法 — 論理削除（deleted flag）"
```

---

### Task 4: 電子帳簿保存法 — タイムスタンプ表示

**Files:**
- Modify: `invoice.html`（セクション1フォームグリッド内にタイムスタンプ表示エリア追加）
- Modify: `invoice.html:1548-1565`（loadInvoice — timestamp表示）
- Modify: `invoice.html:1479`（newInvoice — timestamp表示クリア）

**Step 1: タイムスタンプ表示エリアをHTMLに追加**

`invoice.html:827`（`</select>` の直後、`</div>` 2つで `form-group` と `form-grid` が閉じる前）の付近を確認し、`form-grid` の閉じ `</div>` の直前、つまり `section-card` のフォームグリッドの最後の `form-group` の後に追加する。

具体的には `invoice.html` でステータスselectを含む `<div class="form-group">` の `</div>` 直後に以下を追加：

```html
<div class="form-group full" id="timestampArea" style="font-size:11px;color:var(--text-muted);display:none;padding:4px 0;border-top:1px solid var(--glass-border);margin-top:4px;">
    <span id="tsCreated"></span>
    <span id="tsUpdated" style="margin-left:16px;"></span>
    <span id="tsLocked" style="margin-left:16px;color:#e91e63;"></span>
</div>
```

正確な挿入位置は `invStatus` の `<select>` を含む `<div class="form-group">` の閉じ `</div>` の直後（行828付近）。

**Step 2: タイムスタンプ表示関数を追加**

`applyLockUI` 関数の直後に追加：

```js
function formatTs(ts) {
    if (!ts) return '';
    const d = ts.toDate ? ts.toDate() : new Date(ts);
    return d.toLocaleDateString('ja-JP') + ' ' + d.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
}

function showTimestamps(data) {
    const area = document.getElementById('timestampArea');
    if (!area) return;
    const created  = data.createdAt  ? '作成: ' + formatTs(data.createdAt)  : '';
    const updated  = data.updatedAt  ? '更新: ' + formatTs(data.updatedAt)  : '';
    const locked   = data.lockedAt   ? '🔒 確定: ' + formatTs(data.lockedAt) : '';
    document.getElementById('tsCreated').textContent  = created;
    document.getElementById('tsUpdated').textContent  = updated;
    document.getElementById('tsLocked').textContent   = locked;
    area.style.display = (created || updated || locked) ? '' : 'none';
}
```

**Step 3: loadInvoice でタイムスタンプ表示**

`invoice.html` の `applyLockUI(!!(data.locked));` の直後に追加：

```js
showTimestamps(data);
```

**Step 4: newInvoice でタイムスタンプ非表示**

`invoice.html:1481`（`clearForm()` の直後）に追加：

```js
const tsArea = document.getElementById('timestampArea');
if (tsArea) tsArea.style.display = 'none';
```

**Step 5: 目視確認**

1. 既存の請求書を開く → フォーム上部に「作成: 2026/03/20 19:xx　更新: ...」が表示される
2. 確定済み請求書を開く → 「🔒 確定: 2026/03/20 ...」がピンク色で表示される
3. 「＋ 新規作成」を押す → タイムスタンプエリアが非表示になる

**Step 6: Commit**

```bash
git add invoice.html
git commit -m "feat(compliance): 電子帳簿保存法 — 作成・更新・確定日時の表示"
```

---

### Task 5: 電子帳簿保存法 — 検索機能強化（月・金額フィルター）

**Files:**
- Modify: `invoice.html:777-787`（サイドバーHTML）
- Modify: `invoice.html:1463-1474`（filterInvoiceList）

**Step 1: サイドバーにフィルターUIを追加**

`invoice.html:780`（`<input ... id="searchBox" ...>` の直後）に追加：

```html
<div style="display:flex;gap:4px;margin-top:6px;">
    <select id="filterYear" onchange="filterInvoiceList()" style="flex:1;font-size:11px;background:var(--glass);border:1px solid var(--glass-border);color:var(--text);border-radius:6px;padding:4px;">
        <option value="">年</option>
    </select>
    <select id="filterMonth" onchange="filterInvoiceList()" style="flex:1;font-size:11px;background:var(--glass);border:1px solid var(--glass-border);color:var(--text);border-radius:6px;padding:4px;">
        <option value="">月</option>
        <option value="01">1月</option><option value="02">2月</option><option value="03">3月</option>
        <option value="04">4月</option><option value="05">5月</option><option value="06">6月</option>
        <option value="07">7月</option><option value="08">8月</option><option value="09">9月</option>
        <option value="10">10月</option><option value="11">11月</option><option value="12">12月</option>
    </select>
</div>
<div style="display:flex;gap:4px;margin-top:4px;align-items:center;">
    <input type="number" id="filterAmtMin" placeholder="金額(以上)" min="0" onchange="filterInvoiceList()"
           style="flex:1;font-size:11px;background:var(--glass);border:1px solid var(--glass-border);color:var(--text);border-radius:6px;padding:4px;">
    <span style="color:var(--text-muted);font-size:11px;">〜</span>
    <input type="number" id="filterAmtMax" placeholder="金額(以下)" min="0" onchange="filterInvoiceList()"
           style="flex:1;font-size:11px;background:var(--glass);border:1px solid var(--glass-border);color:var(--text);border-radius:6px;padding:4px;">
</div>
```

**Step 2: 年セレクトの選択肢を動的に生成**

`subscribeInvoices` のコールバック内（`renderInvoiceList(list)` の直後）に追加：

```js
// 年セレクトを動的更新
const years = [...new Set(invoiceCache
    .map(inv => (inv.billingMonth || inv.invDate || '').substring(0, 4))
    .filter(y => y.length === 4)
)].sort().reverse();
const yearSel = document.getElementById('filterYear');
if (yearSel) {
    const cur = yearSel.value;
    yearSel.innerHTML = '<option value="">年</option>' +
        years.map(y => `<option value="${y}"${y === cur ? ' selected' : ''}>${y}年</option>`).join('');
}
```

**Step 3: filterInvoiceList を更新**

`invoice.html:1463-1474` の `filterInvoiceList` 関数全体を以下に置き換える：

```js
function filterInvoiceList() {
    const q        = (document.getElementById('searchBox').value || '').trim().toLowerCase();
    const year     = (document.getElementById('filterYear')?.value  || '');
    const month    = (document.getElementById('filterMonth')?.value || '');
    const amtMin   = parseFloat(document.getElementById('filterAmtMin')?.value) || 0;
    const amtMax   = parseFloat(document.getElementById('filterAmtMax')?.value) || Infinity;

    let base = currentCustomerFilter
        ? invoiceCache.filter(inv => inv.clientName === currentCustomerFilter)
        : invoiceCache;

    if (q)     base = base.filter(inv =>
        (inv.clientName    || '').toLowerCase().includes(q) ||
        (inv.invoiceNumber || '').toLowerCase().includes(q));
    if (year)  base = base.filter(inv => (inv.billingMonth || inv.invDate || '').startsWith(year));
    if (month) base = base.filter(inv => (inv.billingMonth || inv.invDate || '').substring(5, 7) === month);
    if (amtMin > 0)         base = base.filter(inv => (inv.total || 0) >= amtMin);
    if (amtMax < Infinity)  base = base.filter(inv => (inv.total || 0) <= amtMax);

    renderInvoiceList(base);
}
```

**Step 4: 目視確認**

1. サイドバーに「年」「月」セレクト + 金額フィルターが表示されている
2. 年を選ぶと該当年の請求書のみ表示
3. 金額「10000以上」を入力すると合計1万円以上の請求書のみ表示

**Step 5: Commit**

```bash
git add invoice.html
git commit -m "feat(compliance): 電子帳簿保存法 — サイドバーに月・金額フィルター追加"
```

---

## 完了後の確認チェックリスト

### インボイス制度
- [ ] PDFフッターが「10%対象税抜額 / 消費税(10%) / 合計」になっている
- [ ] テーブル下に「消費税率10%適用 / 登録番号：T9120001205370」の注記がある
- [ ] 登録番号が自社欄に表示されている（既存）

### 電子帳簿保存法
- [ ] 「🔒 確定」ボタンが保存ボタンの横にある
- [ ] 確定後にフォームが編集不可になる
- [ ] 確定済み請求書は削除できない（トーストでブロック）
- [ ] Firestoreに `locked: true` / `lockedAt` が保存されている
- [ ] Firestoreに `audit_log` ドキュメントが作成されている
- [ ] 削除後にFirestoreのドキュメントが `deleted: true` で残っている（消えていない）
- [ ] 請求書を開くとフォーム上部に作成・更新日時が表示される
- [ ] 確定済みは「🔒 確定: 日時」がピンクで表示される
- [ ] サイドバーに年・月セレクトと金額フィルターがある
- [ ] 月・金額でフィルタリングが動作する
