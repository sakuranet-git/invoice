# SAKURA 請求書システム — SAKURA-NET デザイン差分適用

**日付:** 2026-03-20
**方針:** 差分適用（既存の実装を活かし、未実装箇所のみ追加）

---

## 背景

`invoice.html` には SAKURA-NET スタイルの多くが既に実装済み（CSS変数・ヘッダーグラスモーフィズム・ボタングロー・cubicベジェ等）。
Gemini の設計指示書 (`design_instruction_for_claude_code.md`) と照合し、未実装の6項目を差分適用する。

---

## 変更項目

### 1. `body` 背景 — 放射状グラデーション追加
```css
body {
    background:
        radial-gradient(ellipse at 20% 50%, rgba(124,58,237,0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(233,30,99,0.06) 0%, transparent 50%),
        var(--bg-dark);
}
```

### 2. `.sidebar` 背景 — 透過グラデーションに変更
```css
.sidebar {
    background: linear-gradient(180deg, rgba(61,0,31,0.7), rgba(26,0,16,0.8));
}
```

### 3. `.inv-card` ホバー — 浮き上がり + グロー追加
```css
.inv-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(233,30,99,0.15);
    border-color: var(--glass-border);
    background: rgba(255,255,255,0.08);
}
```

### 4. `.section-card` — border-radius 16px に拡大
```css
--radius: 16px;  /* :root 変数を更新 */
```

### 5 & 6. `input/select/textarea` + `.search-input` フォーカス — ピンクグロー追加
```css
input:focus, select:focus, textarea:focus {
    border-color: var(--pink);
    box-shadow: 0 0 0 3px rgba(233,30,99,0.15);
}
.search-input:focus {
    border-color: var(--pink);
    box-shadow: 0 0 0 3px rgba(233,30,99,0.15);
}
```

---

## 技術的制約

- Vanilla JS / HTML5 / CSS3 のみ（フレームワーク不使用）
- Firebase V8 ロジック変更なし
- `pi-page` クラス（PDF出力）のスタイルは変更なし
