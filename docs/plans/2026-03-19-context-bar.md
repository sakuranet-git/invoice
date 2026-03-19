# コンテキストバー実装プラン

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 顧客選択後のメインエリアに「選択中の顧客名」と「新規作成中 / 編集中：No.XXXX」を常時表示するコンテキストバーを追加する。

**Architecture:** invoice.html 単一ファイルのみ変更。CSS追加 → HTML追加 → JS ヘルパー追加 → 各関数から呼び出しの順に実装。

**Tech Stack:** HTML/CSS/JavaScript（フレームワークなし）

---

### Task 1: CSS追加（`.context-bar` スタイル）

**Files:**
- Modify: `invoice.html`（`.toolbar` スタイルの直前、約181行目付近）

**Step 1: `.toolbar` の直前に以下CSSを追加**

```css
        /* ===== コンテキストバー ===== */
        .context-bar {
            display: none;
            align-items: center;
            justify-content: space-between;
            padding: 8px 20px;
            background: linear-gradient(135deg, rgba(233,30,99,0.12), rgba(124,58,237,0.12));
            border-left: 3px solid #e91e63;
            border-bottom: 1px solid var(--glass-border);
            font-size: 13px;
        }
        .context-bar.visible { display: flex; }
        .context-bar-name {
            font-weight: 700;
            color: #fff;
        }
        .context-bar-badge {
            font-size: 11px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 20px;
            background: rgba(255,255,255,0.12);
            color: #fff;
        }
        .context-bar-badge.editing {
            background: rgba(233,30,99,0.35);
        }
```

**Step 2: 確認**

ファイルを再読して `.context-bar` スタイルが挿入されていること。

**Step 3: Commit**

```bash
git add invoice.html
git commit -m "feat: コンテキストバー CSS追加"
```

---

### Task 2: HTMLにコンテキストバーを追加

**Files:**
- Modify: `invoice.html`（`.main-area` 直下のツールバー `<div class="toolbar">` の直前、約726行目）

**Step 1: `<!-- ツールバー -->` コメントの直前に以下を挿入**

```html
        <!-- コンテキストバー -->
        <div class="context-bar" id="contextBar">
            <span class="context-bar-name" id="contextBarName"></span>
            <span class="context-bar-badge" id="contextBarBadge"></span>
        </div>

```

**Step 2: 確認**

ファイルを再読して `#contextBar` が `<!-- ツールバー -->` の直前にあること。

**Step 3: Commit**

```bash
git add invoice.html
git commit -m "feat: コンテキストバー HTML追加"
```

---

### Task 3: `updateContextBar()` ヘルパー関数を追加

**Files:**
- Modify: `invoice.html`（`openCustomerInvoices` 関数の直前、約1099行目付近）

**Step 1: `openCustomerInvoices` の直前に以下を挿入**

```js
    // ─────────────────────────────────────────
    // コンテキストバー更新
    // ─────────────────────────────────────────
    function updateContextBar(mode, invoiceNumber) {
        const bar   = document.getElementById('contextBar');
        const name  = document.getElementById('contextBarName');
        const badge = document.getElementById('contextBarBadge');

        if (!currentCustomerFilter) {
            bar.classList.remove('visible');
            return;
        }

        name.textContent = '👤 ' + currentCustomerFilter;

        if (mode === 'new') {
            badge.textContent = '＋ 新規作成中';
            badge.classList.remove('editing');
        } else {
            badge.textContent = '✏ 編集中：No.' + (invoiceNumber || '');
            badge.classList.add('editing');
        }

        bar.classList.add('visible');
    }

```

**Step 2: 確認**

ファイルを再読して `updateContextBar` 関数が存在すること。

**Step 3: Commit**

```bash
git add invoice.html
git commit -m "feat: updateContextBar ヘルパー関数追加"
```

---

### Task 4: 各関数から `updateContextBar()` を呼び出す

**Files:**
- Modify: `invoice.html`（`newInvoice`, `loadInvoice`, `backToCustomers` 関数内）

#### 4-1: `newInvoice()` の末尾に追加

`newInvoice` 関数の末尾（`addItem()` / `updateTotals()` の後、顧客情報自動入力ブロックの後）に追加：

変更前（関数末尾付近）:
```js
        if (currentCustomerFilter && currentCustomerData) {
            const c = currentCustomerData;
            document.getElementById('clientName').value    = c.name    || '';
            document.getElementById('clientContact').value = c.tel1 || c.tel2 || '';
            document.getElementById('clientEmail').value   = c.email   || '';
            document.getElementById('clientAddress').value = (c.zip ? '〒' + c.zip + ' ' : '') + (c.address || '');
        }
    }
```

変更後:
```js
        if (currentCustomerFilter && currentCustomerData) {
            const c = currentCustomerData;
            document.getElementById('clientName').value    = c.name    || '';
            document.getElementById('clientContact').value = c.tel1 || c.tel2 || '';
            document.getElementById('clientEmail').value   = c.email   || '';
            document.getElementById('clientAddress').value = (c.zip ? '〒' + c.zip + ' ' : '') + (c.address || '');
        }
        updateContextBar('new');
    }
```

#### 4-2: `loadInvoice()` の末尾に追加

`loadInvoice` 関数内、`renderItems` / `updateTotals` の後の末尾付近に追加。
`updateTotals();` の直後に：

```js
            updateContextBar('edit', data.invoiceNumber);
```

具体的には以下の箇所を探す：
```js
            renderItems(data.items || []);
            updateTotals();
```
を：
```js
            renderItems(data.items || []);
            updateTotals();
            updateContextBar('edit', data.invoiceNumber);
```
に変更。

#### 4-3: `backToCustomers()` に追加

`backToCustomers` 関数内、`currentCustomerFilter = null;` の直後に追加：

変更前:
```js
    function backToCustomers() {
        currentCustomerFilter = null;
        currentCustomerData   = null;
```

変更後:
```js
    function backToCustomers() {
        currentCustomerFilter = null;
        currentCustomerData   = null;
        updateContextBar('new');
```

**Step 2: 確認**

3箇所すべてに `updateContextBar` の呼び出しが追加されていること。

**Step 3: Commit & Push**

```bash
git add invoice.html
git commit -m "feat: コンテキストバー 各関数から呼び出し追加"
git push origin main
```
