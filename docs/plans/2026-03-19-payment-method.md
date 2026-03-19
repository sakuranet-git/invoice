# 支払い方法フィールド追加 実装プラン

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 請求書フォームの住所フィールド直下に支払い方法プルダウンを追加し、Firestoreへの保存・復元に対応する。

**Architecture:** invoice.html 単一ファイルのみ変更。フォームHTML追加 → collectFormData() 追加 → clearForm() / loadInvoice() / duplicateInvoice() 復元対応の順に実装する。

**Tech Stack:** HTML/CSS/JavaScript, Firebase Firestore v8

---

### Task 1: フォームHTMLにプルダウンを追加

**Files:**
- Modify: `invoice.html:794-797`（住所フィールドの直後）

**Step 1: 住所フィールドの直後に form-group を挿入**

`clientAddress` の `</div>` 直後（約797行目）に以下を追加：

```html
                    <div class="form-group full">
                        <label>支払い方法</label>
                        <select id="paymentMethod">
                            <option value="">（未選択）</option>
                            <option value="クレジットカード払い">クレジットカード払い</option>
                            <option value="口座振替払い">口座振替払い</option>
                            <option value="請求書払い">請求書払い</option>
                            <option value="電子決済払い">電子決済払い</option>
                            <option value="QRコード払い">QRコード払い</option>
                            <option value="その他">その他</option>
                        </select>
                    </div>
```

**Step 2: ブラウザで確認**

- 住所の下に「支払い方法」プルダウンが表示されること
- 6種類の選択肢が表示されること

**Step 3: Commit**

```bash
git add invoice.html
git commit -m "feat: 支払い方法プルダウンをフォームに追加"
```

---

### Task 2: clearForm() にリセット処理を追加

**Files:**
- Modify: `invoice.html:1739`（clearForm 関数内の配列）

**Step 1: clearForm の id 配列に paymentMethod を追加**

変更前：
```js
['invNumber','invDate','clientName','clientContact','clientEmail','clientAddress','invNote'].forEach(id => {
    document.getElementById(id).value = '';
});
document.getElementById('invStatus').value = 'draft';
```

変更後：
```js
['invNumber','invDate','clientName','clientContact','clientEmail','clientAddress','invNote'].forEach(id => {
    document.getElementById(id).value = '';
});
document.getElementById('invStatus').value = 'draft';
document.getElementById('paymentMethod').value = '';
```

**Step 2: 確認**

新規作成ボタンを押すとプルダウンが「（未選択）」に戻ること。

**Step 3: Commit**

```bash
git add invoice.html
git commit -m "feat: clearForm に支払い方法リセットを追加"
```

---

### Task 3: collectFormData() に paymentMethod を追加

**Files:**
- Modify: `invoice.html:1429`（clientAddress の次行）

**Step 1: clientAddress の直後に paymentMethod を追加**

変更前：
```js
clientAddress:  document.getElementById('clientAddress').value.trim(),
note:           document.getElementById('invNote').value.trim(),
```

変更後：
```js
clientAddress:  document.getElementById('clientAddress').value.trim(),
paymentMethod:  document.getElementById('paymentMethod').value,
note:           document.getElementById('invNote').value.trim(),
```

**Step 2: 確認**

保存後にFirestoreコンソールでドキュメントに `paymentMethod` フィールドが入っていること。

**Step 3: Commit**

```bash
git add invoice.html
git commit -m "feat: collectFormData に支払い方法を追加"
```

---

### Task 4: loadInvoice() に復元処理を追加

**Files:**
- Modify: `invoice.html:1357`（clientAddress セットの直後）

**Step 1: clientAddress のセット直後に paymentMethod をセット**

変更前：
```js
document.getElementById('clientAddress').value    = data.clientAddress  || '';
document.getElementById('invNote').value          = data.note           || '';
```

変更後：
```js
document.getElementById('clientAddress').value    = data.clientAddress  || '';
document.getElementById('paymentMethod').value    = data.paymentMethod  || '';
document.getElementById('invNote').value          = data.note           || '';
```

**Step 2: 確認**

保存済み請求書を左メニューから開いたとき、支払い方法が正しく復元されること。

**Step 3: Commit**

```bash
git add invoice.html
git commit -m "feat: loadInvoice に支払い方法の復元を追加"
```

---

### Task 5: duplicateInvoice() に引き継ぎ処理を追加

**Files:**
- Modify: `invoice.html:1326`（clientAddress の複写直後）

**Step 1: clientAddress の複写直後に paymentMethod を追加**

変更前：
```js
document.getElementById('clientAddress').value = src.clientAddress || '';
document.getElementById('invNote').value       = src.note          || '';
```

変更後：
```js
document.getElementById('clientAddress').value = src.clientAddress  || '';
document.getElementById('paymentMethod').value = src.paymentMethod  || '';
document.getElementById('invNote').value       = src.note           || '';
```

**Step 2: 確認**

複写機能で支払い方法が引き継がれること。

**Step 3: Final commit & push**

```bash
git add invoice.html
git commit -m "feat: duplicateInvoice に支払い方法の引き継ぎを追加"
git push origin main
```
