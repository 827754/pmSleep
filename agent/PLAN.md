# だいふくスクレイピング改修計画 (dc)

## 1. 背景・目的

現在 `daifuku_firebase_new.py`（個体値チェック）と `daifuku_firebase_food.py`（期待値チェック）の2ファイルに分かれており、コードの重複が多い。
さらに、サイト側がLv70対応したこと、毎日の再調査需要、他サイトへの拡張性などを考慮し、共通化と新形式 `dc` への移行を行う。

## 2. 現状構成

| ファイル | 役割 | URL |
|---|---|---|
| `daifuku_firebase_new.py` | 個体値評価(rate)取得 | `/checker/` |
| `daifuku_firebase_food.py` | 期待値(f/s/be)取得 | `/checker/expected/` |
| `pokedata.json` | ポケモン名↔IDマッピング | - |
| `evolution.json` | 進化データ | - |
| `{uid}.json` | ユーザーレコード（入出力兼用） | - |

### 現状のデータフロー
```
{uid}.json --[new.py]--> record["new_d"] に個体値データをJSON文字列で保存
{uid}.json --[food.py]--> record["new_d"] に f30/f60/s30/s60/be30/be60 を追記
```

### 新しいデータ構造 `dc`
```json
[
  {
    "name": "メガニウム",
    "forte": "①",
    "Lvs": [
      { "Lv": "30", "rate": "B：58.35%", "f": [...], "s": [...], "be": "..." },
      { "Lv": "60", "rate": "B：58.35%", "f": [...], "s": [...], "be": "..." },
      { "Lv": "70", "rate": "B：58.35%", "f": [...], "s": [...], "be": "..." }
    ]
  }
]
```

## 3. 改修方針

### 3.1 モジュール分割
- **`common/poke_utils.py`**
  - `get_pokemon_last_evolution()`
  - `get_pokemon_evolution_cnt()`
  - `get_totricity()`
  - `replaceUnknown()`
  - `ingredientSkipList`
  - 進化データ・ポケモンデータの読み込み

- **`common/selenium_utils.py`**
  - `close_ad_if_exists()`
  - WebDriverの共通セットアップ

- **`sites/daifuku.py`**
  - だいふく氏サイト固有の操作
  - `pokemonSelect()`
  - `select_ingredient()`
  - ページURL・セレクタ定数
  - 結果テーブルのパース処理

- **`scraper.py`**
  - メインエントリポイント
  - 個体値・期待値の取得フローを統合
  - Lv30/60/70のループ取得
  - `dc` 形式でのデータ構築・保存

- **`config.py`**
  - UIDリスト、調整日次上限、再調査間隔などの設定

### 3.2 新規機能
1. **Lv70対応**
   - `levelDisplay`/`levelSlider` を使い Lv30/60/70 を順次切り替えて取得
2. **毎日の再調査**
   - `--full-research` フラグ または日次バッチ対応
   - すでに `dc` が存在するレコードも、古い更新日時のものから優先的に再調査
   - 1実行あたりの上限件数を設定可能に
3. **出力切り替え**
   - `new_d`（旧）は維持、`dc`（新）を別フィールドとして追加
   - または移行完了後に `new_d` を削除（要相談）

### 3.3 その他改善
- headless/通常モードを設定で切り替え可能に
- 待機時間を適正化（sleepの固定値を減らし、WebDriverWait活用）
- 実行ログ出力の改善

## 4. 作業順序

| # | 作業 | 備考 |
|---|---|---|
| 1 | ユーザー確認（不明点リスト） | 本PLANと同時提出 |
| 2 | `common/` `sites/` ディレクトリ作成、共通関数移行 | 影響が少ない部分から |
| 3 | `scraper.py`（個体値取得部分）作成 | `new.py` と同等の動作 |
| 4 | `scraper.py` に期待値取得・Lv70対応を統合 | `food.py` の機能を統合 |
| 5 | `dc` 形式での出力対応 | `record["dc"]` に保存 |
| 6 | 再調査ロジック実装 | 日次上限・優先順位 |
| 7 | バッチ実行テスト | `{uid}.json` のバックアップ必須 |
| 8 | 旧ファイルを `old/` に移動またはリネーム | クリーンアップ |

## 5. ブランチ情報

- **ブランチ名:** `feature/dc-refactor`
- **ベース:** `main` (6dd15b0)
- **備考:** `evolution.json` が modified 状態なので、作業開始前に現状を確認・コミットするか要検討
