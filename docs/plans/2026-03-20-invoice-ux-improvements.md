# 請求書 UX 改善 3機能 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 顧客グリッドの折りたたみ・支払い方法カラーコード・顧客カードD&D並び替えの3機能を invoice.html に追加する

**Architecture:** 単一HTMLファイル（invoice.html）のみ変更。外部ライブラリ追加なし。localStorage でUI状態を永続化。

**Tech Stack:** HTML5 Drag & Drop API, CSS transition, localStorage

---

## Task 1: 顧客グリッド折りたたみトグル

**Files:**
- Modify: `C:\Users\MYPC\Development\請求書\invoice.html`

### Step 1: CSS追加 — `.customer-grid-wrap` にトランジション設定

`.cust-card-footer` のCSS定義（約681行付近）の直後、`/* 月別ヘッダー */` の前に以下を追加：

```css
/* 顧客グリッド折りたたみ */
.customer-grid-wrap {
    transition: max-height 0.35s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.25s ease;
    overflow: hidden;
}
.customer-grid-wrap.collapsed {
    max-height: 0 !important;
    opacity: 0;
}
.customer-grid-wrap:not(.collapsed) {
    max-height: 2000px;
    opacity: 1;
}
.toggle-grid-btn {
    background: none;
    border: 1px solid var(--glass-border);
    border-radius: 8px;
    color: var(--text-muted);
    padding: 4px 10px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
}
.toggle-grid-btn:hover { border-color: var(--pink); color: var(--text); }
```

### Step 2: HTML変更 — ヘッダーにトグルボタン追加

`#customerView` 内の `.customer-view-header`（718行付近）を以下に変更：

```html
<div class="customer-view-header">
    <h2>👥 顧客一覧</h2>
    <input type="text" class="search-input" id="customerSearch"
           placeholder="顧客名・電話番号で検索..."
           oninput="renderCustomerGrid(this.value)"
           style="width:260px;">
    <button class="toggle-grid-btn" id="toggleGridBtn" onclick="toggleCustomerGrid()">▲ 折りたたむ</button>
</div>
```

### Step 3: JS追加 — `toggleCustomerGrid()` 関数

`renderCustomerGrid()` 関数の直前に追加：

```js
// ─────────────────────────────────────────
// 顧客グリッド折りたたみ
// ─────────────────────────────────────────
function toggleCustomerGrid() {
    const wrap = document.querySelector('.customer-grid-wrap');
    const btn  = document.getElementById('toggleGridBtn');
    const isCollapsed = wrap.classList.toggle('collapsed');
    btn.textContent = isCollapsed ? '▼ 展開する' : '▲ 折りたたむ';
    localStorage.setItem('sakura_grid_collapsed', isCollapsed ? '1' : '0');
}

function restoreGridCollapse() {
    if (localStorage.getItem('sakura_grid_collapsed') === '1') {
        const wrap = document.querySelector('.customer-grid-wrap');
        const btn  = document.getElementById('toggleGridBtn');
        wrap.classList.add('collapsed');
        btn.textContent = '▼ 展開する';
    }
}
```

### Step 4: 初期化処理に `restoreGridCollapse()` 追加

`window.addEventListener('DOMContentLoaded', ...)` 内、`initApp()` 呼び出しの直前（または直後）に追加：

```js
restoreGridCollapse();
```

### Step 5: 動作確認

- ページをリロード → ▲ 折りたたむ ボタンが表示されること
- クリック → グリッドがアニメーション付きで折りたたまれ、ボタンが「▼ 展開する」になること
- 再クリック → グリッドが展開されること
- リロード → 折りたたみ状態が復元されること

### Step 6: Commit

```bash
cd "C:\Users\MYPC\Development\請求書"
git add invoice.html
git commit -m "feat: add customer grid collapse toggle"
```

---

## Task 2: 支払い方法カラーコード（サイドバー請求書アイテム）

**Files:**
- Modify: `C:\Users\MYPC\Development\請求書\invoice.html`

### Step 1: JS追加 — 支払い方法カラーマップ定数

`renderInvoiceList()` 関数の先頭（`const statusMap = ...` の直前）に追加：

```js
const paymentColorMap = {
    '口座振替払い':       '#3b82f6',   // 青（銀行・振込）
    'クレジットカード払い': '#f59e0b',  // アンバー（カード）
    '請求書払い':         '#a78bfa',   // 紫（書類）
    '電子決済払い':       '#06b6d4',   // シアン（デジタル）
    'QRコード払い':       '#f97316',   // オレンジ
    'その他':             '#6b7280',   // グレー
};
```

### Step 2: JS変更 — `renderInvoiceList()` の `.inv-card` にカラーボーダー適用

**変更対象箇所が2つある（顧客フィルター時の月別表示 と 通常表示）。両方を同じように変更する。**

月別表示（1296行付近）の `return` テンプレートを変更：

```js
// 変更前
return `
<div class="inv-card ${isActive}" onclick="loadInvoice('${inv.id}')">

// 変更後
const pmColor = paymentColorMap[inv.paymentMethod] || '';
const pmStyle = pmColor ? `border-left: 3px solid ${pmColor};` : '';
return `
<div class="inv-card ${isActive}" style="${pmStyle}" onclick="loadInvoice('${inv.id}')">
```

通常表示（1317行付近）も同様に変更：

```js
// 変更前
return `
<div class="inv-card ${isActive}" onclick="loadInvoice('${inv.id}')">

// 変更後
const pmColor = paymentColorMap[inv.paymentMethod] || '';
const pmStyle = pmColor ? `border-left: 3px solid ${pmColor};` : '';
return `
<div class="inv-card ${isActive}" style="${pmStyle}" onclick="loadInvoice('${inv.id}')">
```

### Step 3: 動作確認

- 支払い方法を「口座振替払い」に設定して保存 → サイドバーのアイテムの左端に青のボーダーが表示されること
- 「クレジットカード払い」→ アンバー（金色）
- 未設定（空） → ボーダーなし（デフォルト）

### Step 4: Commit

```bash
git add invoice.html
git commit -m "feat: add payment method color coding to invoice list"
```

---

## Task 3: 顧客カード ドラッグ&ドロップ並び替え

**Files:**
- Modify: `C:\Users\MYPC\Development\請求書\invoice.html`

### Step 1: CSS追加 — D&Dビジュアルフィードバック

Task 1 のCSS追加箇所の後ろに追加：

```css
/* D&D 並び替え */
.cust-card[draggable="true"] { cursor: grab; }
.cust-card[draggable="true"]:active { cursor: grabbing; }
.cust-card.dragging { opacity: 0.4; transform: scale(0.97); }
.cust-card.drag-over { border-color: var(--pink); box-shadow: 0 0 0 2px rgba(233,30,99,0.4); }
```

### Step 2: JS追加 — 順序管理ヘルパー関数

`renderCustomerGrid()` 関数の直前に追加：

```js
// ─────────────────────────────────────────
// 顧客カード並び替え（D&D）
// ─────────────────────────────────────────
const CUSTOMER_ORDER_KEY = 'sakura_customer_order';

function loadCustomerOrder() {
    try { return JSON.parse(localStorage.getItem(CUSTOMER_ORDER_KEY)) || []; }
    catch { return []; }
}

function saveCustomerOrder(names) {
    localStorage.setItem(CUSTOMER_ORDER_KEY, JSON.stringify(names));
}

function applyCustomerOrder(customers) {
    const order = loadCustomerOrder();
    if (order.length === 0) return customers;
    const map = new Map(customers.map(c => [c.name, c]));
    const sorted = order.map(n => map.get(n)).filter(Boolean);
    // 順序に含まれていない顧客（新規追加分）は末尾に追加
    customers.forEach(c => { if (!order.includes(c.name)) sorted.push(c); });
    return sorted;
}
```

### Step 3: JS変更 — `renderCustomerGrid()` でD&D有効化

`renderCustomerGrid()` 関数内の `let customers = customerCache;` の直後を変更：

```js
// 変更前
let customers = customerCache;
if (q) {
    customers = customers.filter(...);
}

// 変更後
let customers = customerCache;
if (q) {
    customers = customers.filter(c =>
        (c.name   || '').toLowerCase().includes(q) ||
        (c.agency || '').toLowerCase().includes(q) ||
        (c.tel1   || '').includes(q) ||
        (c.tel2   || '').includes(q)
    );
} else {
    // 検索なし時のみ並び替え適用
    customers = applyCustomerOrder(customers);
}
```

### Step 4: JS変更 — `.cust-card` に draggable と D&Dイベント追加

`renderCustomerGrid()` 内の `grid.innerHTML = customers.map(c => { ... }).join('');` の直後（`}`の閉じ括弧の前）に以下を追加：

```js
// D&Dイベントを各カードに登録
let dragSrcName = null;
grid.querySelectorAll('.cust-card').forEach(card => {
    card.setAttribute('draggable', 'true');

    card.addEventListener('dragstart', e => {
        dragSrcName = card.dataset.name;
        card.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
    });
    card.addEventListener('dragend', () => {
        card.classList.remove('dragging');
        grid.querySelectorAll('.cust-card').forEach(c => c.classList.remove('drag-over'));
    });
    card.addEventListener('dragover', e => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        grid.querySelectorAll('.cust-card').forEach(c => c.classList.remove('drag-over'));
        card.classList.add('drag-over');
    });
    card.addEventListener('drop', e => {
        e.preventDefault();
        card.classList.remove('drag-over');
        if (dragSrcName === card.dataset.name) return;

        // DOM上の現在の順序を取得して並び替え
        const cards = [...grid.querySelectorAll('.cust-card')];
        const names = cards.map(c => c.dataset.name);
        const srcIdx  = names.indexOf(dragSrcName);
        const destIdx = names.indexOf(card.dataset.name);
        if (srcIdx === -1 || destIdx === -1) return;

        names.splice(srcIdx, 1);
        names.splice(destIdx, 0, dragSrcName);
        saveCustomerOrder(names);
        renderCustomerGrid(); // 並び替え後に再描画
    });
});
```

### Step 5: 動作確認

- 顧客グリッドでカードをドラッグ → 半透明になること
- 別のカードにドロップ → ピンクのボーダーハイライトが出てドロップ後に並び替わること
- ページをリロード → 並び順が復元されること
- 検索ボックスに文字を入力 → D&Dなし、通常の検索結果表示になること

### Step 6: Commit

```bash
git add invoice.html
git commit -m "feat: add drag-and-drop customer card reordering"
```

---

## 完了後

WinSCPで `/system/invoice/invoice.html` にアップロードして動作確認。
