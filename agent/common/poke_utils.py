"""
ポケモン進化計算・名前解決などの共通ユーティリティ。
pokedata.json / evolution.json を読み込み、進化系の導出等を行う。
"""

import json
import os
import re

# プロジェクトルートパスを設定ファイルから取得
from config import BASE_DIR

# --- プロジェクトルートから JSON を読み込む ---
with open(os.path.join(BASE_DIR, "evolution.json"), "r", encoding="utf-8") as _f:
    evolution_data = json.load(_f)

with open(os.path.join(BASE_DIR, "pokedata.json"), "r", encoding="utf-8") as _f:
    pm_data = json.load(_f)


# ---------------------------------------------------------------------------
# 汎用ヘルパ
# ---------------------------------------------------------------------------
def replace_unknown(val, default, targets=("なし", "不明")):
    """val が targets に含まれれば default に置き換える。（個体値ページ用）"""
    return default if val in targets else val


# ---------------------------------------------------------------------------
# ストリンダー用：性格→姿決定
# ---------------------------------------------------------------------------
def get_totricity(personality):
    """エレズンの性格から進化後のストリンダーの姿を決定する。"""
    high = [
        "いじっぱり", "やんちゃ", "ゆうかん", "なまいき", "うっかりや",
        "わんぱく", "のうてんき", "ようき", "せっかち", "むじゃき",
        "がんばりや", "きまぐれ", "すなお",
    ]
    low = [
        "さみしがり", "しんちょう", "おとなしい", "おだやか", "ずぶとい",
        "のんき", "おっとり", "れいせい", "ひかえめ", "おくびょう",
        "てれや", "まじめ",
    ]

    if personality in high:
        return "ストリンダー（ハイなすがた）"
    elif personality in low:
        return "ストリンダー（ローなすがた）"
    return ""


# ---------------------------------------------------------------------------
# 進化回数取得
# ---------------------------------------------------------------------------
def get_pokemon_evolution_cnt(poke_name):
    """ポケモン名から進化回数（evolve_cnt）を取得する。

    バケッチャ・パンプジン系はサイト側の仕様に合わせて丸め込む。
    見つからない場合は 0 を返す（既存コードと同じ動作）。
    """
    if "バケッチャ" in poke_name:
        poke_name = "バケッチャ（ちゅうだましゅ）"
    if "パンプジン" in poke_name:
        poke_name = "パンプジン（ちゅうだましゅ）"

    tmp_id = None
    for pm_item in pm_data:
        if pm_item["name"] == poke_name:
            tmp_id = int(float(pm_item["id"]))
            break

    for item in evolution_data:
        if str(item["id"]) == str(tmp_id):
            return item.get("evolve_cnt", 0)

    return 0


# ---------------------------------------------------------------------------
# MainLv 計算（進化回数加算後）
# ---------------------------------------------------------------------------
def calc_main_lv(record):
    """レコードから進化回数加算後の MainLv（文字列）を計算して返す。

    ストリンダー系や限定衣装ポケモンの特殊処理も含む。
    """
    main_lv = record.get("mainLv", "1")
    if main_lv in ("0", ""):
        main_lv = "1"

    pokemon = record["pokemon"]
    special = ["ホリデー", "ハロウィン", "キャプテン"]

    if "ストリンダー" in pokemon:
        main_lv = str(int(main_lv) + int(get_pokemon_evolution_cnt(pokemon)))
    elif all(x not in pokemon for x in special):
        main_lv = str(
            int(main_lv) + int(get_pokemon_evolution_cnt(re.sub(r"（.*$", "", pokemon)))
        )

    return main_lv


# ---------------------------------------------------------------------------
# 最終進化系取得
# ---------------------------------------------------------------------------
def get_pokemon_last_evolution(poke_name, personality):
    """ポケモン名と性格から最終進化系（分岐進化なら複数）を返す。

    Returns:
        list[str]: 最終進化候補のポケモン名リスト。
    """
    # 1) 特殊な姿・限定衣装の例外定義（サイト側のセレクトボックスに合わせる）
    special_cases = {
        "ピカチュウ（ハロウィン）": ["ハロウィンピカチュウ"],
        "ピカチュウ（ホリデー）": ["ホリデーピカチュウ"],
        "ピカチュウ(キャプテン)": ["キャプテンピカチュウ"],
        "イーブイ（ハロウィン）": ["ハロウィンイーブイ"],
        "イーブイ（ホリデー）": ["ホリデーイーブイ"],
        "タマザラシ（ホリデー）": ["タマザラシ（ホリデー）"],
        "イーブイ": [
            "シャワーズ", "サンダース", "ブースター", "エーフィ",
            "ブラッキー", "リーフィア", "グレイシア", "ニンフィア",
        ],
        "ヤドン": ["ヤドキング", "ヤドラン"],
        "ロコン": ["キュウコン"],
        "ロコン（アローラのすがた）": ["キュウコン（アローラのすがた）"],
        "ウパー": ["ヌオー"],
        "ウパー（パルデアのすがた）": ["ドオー"],
        "ミュウ": ["ミュウ（スキル得意で仮入力）"],
        "ダークライ": ["ダークライ（スキル得意で仮入力）"],
    }

    if poke_name in special_cases:
        return special_cases[poke_name]

    if poke_name in ("ラルトス", "キルリア"):
        return ["サーナイト", "エルレイド"]

    if poke_name == "エレズン":
        return [get_totricity(personality)]

    # 分岐進化の最終形態はそのまま返す（再調査不要）
    bunki_list = [
        "シャワーズ", "サンダース", "ブースター", "エーフィ", "ブラッキー",
        "リーフィア", "グレイシア", "ニンフィア",
        "ヤドラン", "ヤドキング", "サーナイト", "エルレイド",
        "キュウコン", "キュウコン（アローラのすがた）", "ヌオー", "ドオー",
        "ストリンダー（ハイなすがた）", "ストリンダー（ローなすがた）",
    ]
    if poke_name in bunki_list:
        return [poke_name]

    # バケッチャ・パンプジン系：サイズ（）を維持して進化後を導出
    if "バケッチャ" in poke_name:
        match = re.search(r'（.*?）', poke_name)
        return ["パンプジン" + (match.group(0) if match else "")]
    if "パンプジン" in poke_name:
        return [poke_name]

    # 2) 通常の進化データ検索
    tmp_id = None
    for pm_item in pm_data:
        if pm_item["name"] == poke_name:
            tmp_id = pm_item["id"]
            break

    tmp_name_list = []
    for item in evolution_data:
        if str(item["id"]) == str(tmp_id):
            tmp_name_list = [evo["name"] for evo in item["evolution"]]

    name_list = []
    for name_check in tmp_name_list:
        for pm_item in pm_data:
            if pm_item["name"] == name_check:
                name_list.append(name_check)

    if not name_list:
        return [poke_name]

    # リストの最後を最終進化として返す
    return [name_list[-1]]
