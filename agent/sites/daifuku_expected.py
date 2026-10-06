"""
だいふく氏サイト /checker/expected/ （期待値）ページ固有の処理。
Lv70 → 60 → 30 の順にスライダーで切り替えてチェックを蓄積し、
resultTable から各 Lv の期待値（f / s / be）を取得する。
"""

from time import sleep
from selenium.webdriver.common.by import By

from config import URL_EXPECTED, LEVELS_TO_CHECK
from common.poke_utils import get_pokemon_last_evolution
from sites.daifuku_base import (
    navigate_to,
    pokemon_select,
    select_ingredient,
    select_subskill_by_visible_text,
    select_personality,
    select_main_lv,
    select_evolution_count,
    set_level,
    click_check_button,
    reset_form,
)

# 食材選択をスキップするポケモン（2023年当時の仕様）
INGREDIENT_SKIP_LIST = [
    "ミュウ（スキル得意で仮入力）",
    "ダークライ（スキル得意で仮入力）",
]


# ---------------------------------------------------------------------------
# Lv70 追加サブスキル選択
# ---------------------------------------------------------------------------
def select_subskill4(driver, sub75):
    """Lv を 70 にして subSkill4（pokemon_subskill4）を有効化し選択する。

    サイト側では Lv が 70 の時だけ subSkill4 が enabled になる。
    70→60 に下げると自動的にリセットされるため、
    この関数は Lv70 のチェック直前に呼ぶこと。
    """
    if not sub75:
        return
    set_level(driver, 70)
    sub75 = sub75.replace("げんき", "元気")
    select_subskill_by_visible_text(driver, "pokemon_subskill4", sub75)


# ---------------------------------------------------------------------------
# 結果テーブルパース
# ---------------------------------------------------------------------------
def parse_expected_table(driver):
    """resultTable をパースして期待値データを抽出する。

    期待値ページのテーブル構造（A2回答のHTMLより）:
      tr[0]: ヘッダー行（<td>ポケモン</td><td>スキル名</td>...<td>ポケモンLv</td>）
      tr[1~]: データ行（新しい行が上に蓄積される、最大5件で更新）
        td[0] = ポケモン名
        td[2] = スキル効果      → s[0]
        td[3] = スキル発動回数   → s[1]
        td[4] = スキル効果合計   → s[2]
        td[5] = きのみエナジー   → be
        td[7] = 第一食材数       → f[0]
        td[8] = 第二食材数       → f[1]
        td[9] = 第三食材数       → f[2]
        td[10] = ポケモンLv（30/60/70）

    Returns:
        list[dict]: [
            {"name": "リザードン", "Lv": "30", "f": [...], "s": [...], "be": "..."},
            ...
        ]
    """
    table = driver.find_element(By.CLASS_NAME, "resultTable")
    rows = table.find_elements(By.TAG_NAME, "tr")

    results = []
    for row in rows:
        tds = row.find_elements(By.TAG_NAME, "td")
        # ヘッダー行は td[0] = "ポケモン" 、データ行は td[0] = ポケモン名
        if len(tds) > 10:
            # ヘッダー行を除外（td[0] が "ポケモン" の場合）
            first = tds[0].text.strip()
            if first == "ポケモン":
                continue
            results.append({
                "name": first,
                "Lv": tds[10].text.strip(),
                "f": [tds[7].text.strip(), tds[8].text.strip(), tds[9].text.strip()],
                "s": [tds[2].text.strip(), tds[3].text.strip(), tds[4].text.strip()],
                "be": tds[5].text.strip(),
            })
    return results


# ---------------------------------------------------------------------------
# メイン取得処理
# ---------------------------------------------------------------------------
def fetch_expected_values(driver, record):
    """期待値チェッカーで Lv30/60/70 の期待値を取得する。

    Lv の高い順（70 → 60 → 30）にチェックを蓄積し、
    最後にテーブルを1回パースして全 Lv 分のデータを取得する。

    subSkill4 は Lv=70 のチェック直前に選択する。
    Lv を下げると自動的にリセットされるサイト仕様を利用。

    Args:
        driver: Selenium WebDriver。
        record: 1件のユーザーレコード辞書。

    Returns:
        dict: {ポケモン名: {"name": ..., "Lvs": [{"Lv":"30", ...}, ...]}}
        失敗・スキップ時は空辞書を返す。
    """
    navigate_to(driver, URL_EXPECTED)
    sleep(2)

    # --- 最終進化系リスト導出 ---
    poke_name_list = get_pokemon_last_evolution(record["pokemon"], record["personality"])
    print(f"最終進化候補: {poke_name_list}")

    # --- サブスキル・MainLv準備 ---
    from common.poke_utils import calc_main_lv
    main_lv = calc_main_lv(record)

    sub10 = record.get("sub10", "")
    sub25 = record.get("sub25", "")
    sub50 = record.get("sub50", "")
    sub75 = record.get("sub75", "")  # Lv70追加サブスキル（あれば）

    # --- 初回ポケモン選択 ---
    if not pokemon_select(driver, poke_name_list[0]):
        print("ポケモン選択失敗のためスキップ")
        return {}

    # --- 食材選択（スキップ対象を除く） ---
    if poke_name_list[0] not in INGREDIENT_SKIP_LIST:
        if not select_ingredient(driver, record.get("ingredients30", ""), "pokemon_ingredient2"):
            print("食材2選択失敗のためスキップ")
            return {}
        if not select_ingredient(driver, record.get("ingredients60", ""), "pokemon_ingredient3"):
            print("食材3選択失敗のためスキップ")
            return {}

    # --- MainLv ---
    select_main_lv(driver, main_lv)

    # --- サブスキル（性格に応じて'げんき'→'元気'置換） ---
    # sub1~3 は Lv に関係なく有効
    sub10 = sub10.replace("げんき", "元気")
    sub25 = sub25.replace("げんき", "元気")
    sub50 = sub50.replace("げんき", "元気")
    select_subskill_by_visible_text(driver, "pokemon_subskill1", sub10)
    select_subskill_by_visible_text(driver, "pokemon_subskill2", sub25)
    select_subskill_by_visible_text(driver, "pokemon_subskill3", sub50)

    # --- 性格 ---
    select_personality(driver, record["personality"])

    # --- 進化回数 ---
    select_evolution_count(driver, record["pokemon"])

    # --- 各進化系で Lv70→60→30 をチェック蓄積 ---
    all_data = {}  # {name: {"name": ..., "Lvs": []}}

    for loop_name in poke_name_list:
        if not pokemon_select(driver, loop_name):
            print(f"{loop_name} の選択に失敗、次の進化系へ")
            continue

        # --- Lv の高い順にチェック（70 → 60 → 30） ---
        # Lv=70 のチェック直前に subSkill4 を選択（Lv70専用）
        for lv in LEVELS_TO_CHECK:  # [70, 60, 30]
            if lv == 70:
                select_subskill4(driver, sub75)
            set_level(driver, lv)
            click_check_button(driver)
            sleep(5)

        # --- 全 Lv チェック後にテーブルを1回パース ---
        all_parsed = parse_expected_table(driver)
        lv_entries = []
        for item in all_parsed:
            if item["name"] == loop_name and item["Lv"] in map(str, LEVELS_TO_CHECK):
                lv_entries.append({
                    "Lv": item["Lv"],
                    "f": item["f"],
                    "s": item["s"],
                    "be": item["be"],
                })

        if lv_entries:
            # Lv 昇順に並び替えて格納（30 < 60 < 70）
            lv_entries.sort(key=lambda x: int(x["Lv"]))
            all_data[loop_name] = {
                "name": loop_name,
                "Lvs": lv_entries,
            }

    # --- フォームリセット ---
    reset_form(driver)

    print(f"期待値取得結果: {list(all_data.keys())}")
    return all_data
