"""
だいふくスクレイピングの設定ファイル。
日次上限、UIDリスト、URL、各種定数を管理する。
"""

import os

# --- ベースディレクトリ ---
# 本ファイルは agent/config.py にあるため、親ディレクトリがプロジェクトルート
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- ユーザーデータ(JSON)保存先 ---
DATA_DIR = os.path.join(BASE_DIR, "agent")

# --- 対象UIDリスト ---
# 処理対象のユーザードキュメントID（{uid}.json が DATA_DIR に配置）
UIDS = [
    "lGZ0ragq7IM0JvlvycwfdFThhwh2",
    # "RX24lgz8q6YG5JkrrW7UsJojmqC3",
]

# --- だいふく氏サイトURL ---
URL_CHECKER = "https://www.pokemonsleepdaifuku.com/checker/"          # 個体値評価ページ
URL_EXPECTED = "https://www.pokemonsleepdaifuku.com/checker/expected/"  # 期待値ページ

# --- 再調査設定 ---
DAILY_LIMIT = 1  # 1実行あたりの処理上限件数（日次バッチ等で使用）

# --- Selenium設定 ---
HEADLESS_DEFAULT = False  # True=バックグラウンド実行, False=画面表示あり

# --- データソースファイル ---
EVOLUTION_JSON = "evolution.json"
POKEDATA_JSON = "pokedata.json"

# --- 食材選択をスキップするポケモン ---
# だいふく氏サイトで食材選択ができないポケモンを列挙
INGREDIENT_SKIP_LIST = [
    "ミュウ（スキル得意で仮入力）",
    "ダークライ（スキル得意で仮入力）",
]

# --- メインスキルLvに進化回数を加算しない特殊ポケモンのキーワード ---
SPECIAL_POKEMON_KEYWORDS = ["ホリデー", "ハロウィン", "キャプテン"]

# --- 個体値ページ用：サブスキルが不明时的なデフォルト値 ---
DEFAULT_SUBSKILL_1 = "げんき回復ボーナス"
DEFAULT_SUBSKILL_2 = "リサーチEXPボーナス"
DEFAULT_SUBSKILL_3 = "ゆめのかけらボーナス"

# --- 期待値ページでチェックするレベル一覧 ---
# 高Lvから順に取得することで、ページの状態が安定しやすい
LEVELS_TO_CHECK = [70, 60, 30]
