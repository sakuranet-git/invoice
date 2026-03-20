# SAKURA-NET Design Refresh Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** `invoice.html` の UI に SAKURA-NET デザイン指示書の未実装6項目を差分適用し、グラスモーフィズム・グロー・アニメーションを強化する。

**Architecture:** すべての変更は `invoice.html` の `<style>` ブロック内 CSS のみ。JS・HTML・Firebase・pi-page（PDF出力）は一切触らない。

**Tech Stack:** Vanilla CSS, Google Fonts（既読込済）

---

### Task 1: body 背景に放射状グラデーションを追加

**Files:**
- Modify: `invoice.html:44`

**Step 1: 変更を適用**

`invoice.html` の `body` の `background: var(--bg-dark);` を以下に置き換える：

```css
background:
    radial-gradient(ellipse at 20% 50%, rgba(124,58,237,0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(233,30,99,0.06) 0%, transparent 50%),
    var(--bg-dark);
```

**Step 2: 目視確認**

ブラウザで `invoice.html` を開き、背景に微かなパープル/ピンクの放射状グラデーションが表示されていることを確認。

**Step 3: Commit**

```bash
git add invoice.html
git commit -m "style: add radial gradient to body background"
```

---

### Task 2: サイドバー背景を透過グラデーションに変更

**Files:**
- Modify: `invoice.html:86`

**Step 1: 変更を適用**

`.sidebar` の `background: var(--bg-panel);` を以下に置き換える：

```css
background: linear-gradient(180deg, rgba(61,0,31,0.7), rgba(26,0,16,0.8));
```

**Step 2: 目視確認**

サイドバーが深いダークレッドの透過グラデーションになっていることを確認。body の放射状グラデーションが透けて見えること。

**Step 3: Commit**

```bash
git add invoice.html
git commit -m "style: apply transparent gradient to sidebar background"
```

---

### Task 3: 請求書カードホバーに浮き上がり＋グロー追加

**Files:**
- Modify: `invoice.html:145`

**Step 1: 変更を適用**

`.inv-card:hover { ... }` を以下に置き換える：

```css
.inv-card:hover {
    border-color: var(--glass-border);
    background: rgba(255,255,255,0.08);
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(233,30,99,0.15);
}
```

**Step 2: 目視確認**

サイドバーの請求書カードにマウスオーバーすると、2px 上に浮き上がりピンクのグローが出ることを確認。

**Step 3: Commit**

```bash
git add invoice.html
git commit -m "style: add translateY and glow to inv-card hover"
```

---

### Task 4: --radius 変数を 14px → 16px に拡大

**Files:**
- Modify: `invoice.html:35`

**Step 1: 変更を適用**

`:root` の `--radius: 14px;` を以下に変更：

```css
--radius: 16px;
```

**Step 2: 目視確認**

メインエリアのセクションカード（顧客情報・請求書情報・品目等）の角丸が若干丸くなっていることを確認。

**Step 3: Commit**

```bash
git add invoice.html
git commit -m "style: increase --radius to 16px for rounder section cards"
```

---

### Task 5: 入力フィールドフォーカスにピンクグローを追加

**Files:**
- Modify: `invoice.html:329`
- Modify: `invoice.html:121`
- Modify: `invoice.html:372`

**Step 1: 変更を適用（通常入力）**

`input:focus, select:focus, textarea:focus { border-color: var(--pink); }` を以下に置き換える：

```css
input:focus, select:focus, textarea:focus {
    border-color: var(--pink);
    box-shadow: 0 0 0 3px rgba(233,30,99,0.15);
}
```

**Step 2: 変更を適用（サイドバー検索）**

`.search-input:focus { border-color: var(--pink); }` を以下に置き換える：

```css
.search-input:focus {
    border-color: var(--pink);
    box-shadow: 0 0 0 3px rgba(233,30,99,0.15);
}
```

**Step 3: 変更を適用（品目テーブル内入力）**

`.item-table input:focus { border-color: var(--pink); background: rgba(0,0,0,0.2); }` を以下に置き換える：

```css
.item-table input:focus {
    border-color: var(--pink);
    background: rgba(0,0,0,0.2);
    box-shadow: 0 0 0 3px rgba(233,30,99,0.15);
}
```

**Step 4: 目視確認**

任意の入力フィールドをクリックしたとき、ピンクのボーダーに加えて薄いピンクのグロー（ring）が表示されることを確認。

**Step 5: Commit**

```bash
git add invoice.html
git commit -m "style: add pink focus glow to all input fields"
```

---

## 完了後の確認チェックリスト

- [ ] body 背景に放射状グラデーションが見える
- [ ] サイドバーが透過グラデーション（深いダークレッド）になっている
- [ ] 請求書カードホバーで浮き上がり＋グロー発生
- [ ] セクションカードの角丸が 16px になっている
- [ ] 全入力フィールドのフォーカスでピンクグロー表示
- [ ] PDF 出力（pi-page）のスタイルに変化なし
- [ ] モバイル表示（DevTools）で崩れなし
