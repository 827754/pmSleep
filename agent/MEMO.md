# 引継ぎメモ (dc 改修プロジェクト)

## コミット情報
- ブランチ: `feature/dc-refactor`
- コミット: `533c080`
- 日時: 2026-10-06

## 新モジュール構成
```
agent/
├── config.py              # 設定（UID, URL, 日次上限, LEVELS_TO_CHECK）
├── scraper.py             # メインエントリポイント
├── common/
│   ├── __init__.py
│   ├── poke_utils.py      # 進化計算・最終進化系導出・MainLv計算
│   └── selenium_utils.py  # WebDriverセットアップ・広告クローズ
└── sites/
    ├── __init__.py
    ├── daifuku_base.py    # だいふくサイト共通UI操作
    ├── daifuku_checker.py # /checker/ 個体値ページ
    └── daifuku_expected.py # /checker/expected/ 期待値ページ
```

## 現在の動作状況

### 期待値ページ (`/checker/expected/`)
- ✅ ポケモン選択・食材選択・サブスキル選択・性格・進化回数
- ✅ Lv70→60→30 の順にチェック蓄積
- ✅ Lv=70 の時だけ subSkill4 を選択（下げると自動リセット）
- ✅ テーブルパースで f/s/be を各 Lv 別に取得
- ✅ `dc` 形式で `record["dc"]` に保存

### 個体値ページ (`/checker/`)
- ⚠️ **不具合あり（後述）**

---

## 確認済みの不具合

### 1. 個体値ページで70/60/30のrateが全て取得できていない
**現象:** `dc.Lvs` 内の `rate` が Lv70 にしか設定されていない
```json
"Lvs": [
  {"Lv": "30", "f": [...], "s": [...], "be": "..."},        // rate なし
  {"Lv": "60", "f": [...], "s": [...], "be": "..."},        // rate なし
  {"Lv": "70", "f": [...], "s": [...], "be": "...", "rate": "C：54.57%"} // だけある
]
```

**原因推定:**
- 個体値ページでも Lv を切り替えてチェックしているが、蓄積されたテーブルのパース時に Lv ごとの行を正しく識別できていない可能性
- `parse_checker_table()` が新しい行を上から順に読んでいるが、`build_dc()` での `lv_entry.get("Lv") == lv` のマッチングがうまくいっていない、または `individual_results` に各 Lv のデータが入っていない

### 2. subSkill4 が選択できていない（個体値ページ）
**現象:** Lv=70 のチェックボタン押下前に subSkill4 を選択しようとしているが、有効化されていない

**原因:**
- ポケモンを選んだ直後にレベルを **先に 70 にしないと** subSkill4 の選択肢が enabled にならない
- 現在のコードは subSkill1~3 → 性格 → 進化回数 の後に `set_level(70)` → チェック を行っているが、**subSkill4 の選択まで subSkill1~3 と同じタイミングでやってしまっている**

**修正方針:**
- Lv=70 のチェック直前（`click_check_button` の直前）に `set_level(70)` と `select_subskill4()` を行う必要がある
- subSkill1~3 は共通設定として先に行い、その後 Lv ループ内で set_level + subSkill4(必要時) + click_check とする

### 3. Lv70→60→30 の変更が不安定（個体値ページ）
**現象:** スライダーの操作が効かない、またはテーブルが更新されない場合がある

**原因推定:**
- 個体値ページと期待値ページで `levelSlider` の動作が若干異なる可能性
- テキストボックス `levelDisplay` を直接変更する方が安定する

**修正方針:**
- `set_level()` 関数でスライダー操作の後、テキストボックスの `value` も明示的に設定し、`change` イベントを発火させる
- またはスライダー操作を廃止し、テキストボックスのみを使用する

### 4. 個体値ページと期待値ページのスライダー挙動の違い
- 期待値ページ: スライダー + テキストボックス 両方で Lv 変更が安定
- 個体値ページ: スライダーが不安定（イベント発火のタイミング問題？）

**修正案:**
```python
def set_level(driver, level):
    # テキストボックス中心に変更
    level_input = driver.find_element(By.ID, "levelDisplay")
    level_input.clear()
    level_input.send_keys(str(level))
    # スライダーも合わせておく（表示用）
    slider = driver.find_element(By.ID, "levelSlider")
    driver.execute_script(
        "arguments[0].value = arguments[1];",
        slider, str(level)
    )
    # テキストボックスに change/input イベントを発火
    driver.execute_script(
        "var e = document.getElementById('levelDisplay');"
        "e.dispatchEvent(new Event('input', { bubbles: true }));"
        "e.dispatchEvent(new Event('change', { bubbles: true }));"
    )
    sleep(0.5)
```

---

## 追加で対応が必要な項目

- [ ] **個体値ページの Lv ループ構造の見直し**
  - subSkill1~3 → 性格 → 進化回数 は共通設定
  - その後 Lv ループ: set_level(lv) + (lv==70 の場合 subSkill4 選択) + click_check
  - 最後にテーブルを1回パース

- [ ] **`set_level()` の安定化**
  - スライダー操作を弱め、テキストボックス中心に変更

- [ ] **エラーハンドリング**
  - テスト段階: 1件失敗で終了（現在は try/except なしなので例外で止まる）
  - 最終版: 3件連続失敗で終了（要実装）

- [ ] **DAILY_LIMIT の設定**
  - テスト時は 1 に設定済み。本番は 10 に戻す

---

## 参考: 既存ファイル
- `daifuku_firebase_new.py` → `agent/old/daifuku_firebase_new.py.bak`
- `daifuku_firebase_food.py` → `agent/old/daifuku_firebase_food.py.bak`
- 元の `{uid}.json` → `agent/uid/{uid}.json`
- 最新50件データ → `agent/{uid}.json`
