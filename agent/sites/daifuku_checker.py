"""
だいふく氏サイト /checker/ （個体値評価）ページ固有の処理。
ポケモンを選んで Lv70→60→30 の順にチェック蓄積し、
resultTable から各 Lv の評価（rate）と得意タイプ（forte）を取得する。
"""

from time import sleep
from selenium.webdriver.common.by import By

from config import URL_CHECKER, DEFAULT_SUBSKILL_1, DEFAULT_SUBSKILL_2, DEFAULT_SUBSKILL_3, LEVELS_TO_CHECK
from common.poke_utils import get_pokemon_last_evolution
from common.selenium_utils import close_ad_if_exists
from sites.daifuku_base import (
    navigate_to,
    pokemon_select,
    select_ingredient,
    select_subskill_with_fallback,
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


def parse_checker_table(driver):
    """resultTable をパースして個体値データを抽出する。

    個体値ページのテーブル構造（A3回答のHTMLより）:
      tr[0]: ヘッダー行（<th>ポケモン</th><th>Lv</th><th>総合評価</th><th>得意</th>...）
      tr[1~]: データ行（新しい行が上に蓄積される）
        td[0]=ポケモン名, td[1]=Lv, td[2]=総合評価(rate), td[3]=得意(forte)

    Returns:
        list[dict]: [
            {"name": "リザードン", "Lv": "30", "rate": "B：51.24%", "forte": "⑤"},
            ...
        ]
    """
    table = driver.find_element(By.CLASS_NAME, "resultTable")
    driver.execute_script("arguments[0].scrollIntoView(true);", table)
    rows = table.find_elements(By.TAG_NAME, "tr")

    results = []
    in_data = False
    for row in rows:
        tds = row.find_elements(By.TAG_NAME, "td")
        if len(tds) > 3:
            # データ行
            results.append({
                "name": tds[0].text.strip(),
                "Lv": tds[1].text.strip(),
                "rate": tds[2].text.strip(),
                "forte": tds[3].text.strip(),
            })
    return results


def fetch_individual_rates(driver, record):
    """個体値チェッカーで評価（rate）と得意タイプ（forte）を取得する。

    各 Lv（LEVELS_TO_CHECK の高い順）でチェックを蓄積し、
    最後にテーブルを1回パースして全 Lv 分のデータを取得する。

    Args:
        driver: Selenium WebDriver。
        record: 1件のユーザーレコード辞書。

    Returns:
        list[dict]: [
            {"name": "リザードン", "Lv": "30", "rate": "B：51.24%", "forte": "⑤"},
            {"name": "リザードン", "Lv": "60", "rate": "C：45.81%", "forte": "⑤"},
            {"name": "リザードン", "Lv": "70", "rate": "D：42.67%", "forte": "⑤"},
        ]
        失敗・スキップ時は空リストを返す。
    """
    navigate_to(driver, URL_CHECKER)
    sleep(2)

    # --- 最終進化系リスト導出 ---
    poke_name_list = get_pokemon_last_evolution(record["pokemon"], record["personality"])
    print(f"最終進化候補: {poke_name_list}")

    # --- MainLv（進化回数加算後）を計算 ---
    from common.poke_utils import calc_main_lv
    main_lv = calc_main_lv(record)

    sub10 = record.get("sub10", "")
    sub25 = record.get("sub25", "")
    sub50 = record.get("sub50", "")

    # --- 初回ポケモン選択 ---
    if not pokemon_select(driver, poke_name_list[0]):
        print("ポケモン選択失敗のためスキップ")
        return []

    # --- 食材選択（スキップ対象を除く） ---
    if poke_name_list[0] not in INGREDIENT_SKIP_LIST:
        if not select_ingredient(driver, record.get("ingredients30", ""), "pokemon_ingredient2"):
            print("食材2選択失敗のためスキップ")
            return []
        if not select_ingredient(driver, record.get("ingredients60", ""), "pokemon_ingredient3"):
            print("食材3選択失敗のためスキップ")
            return []

    # --- MainLv ---
    select_main_lv(driver, main_lv)

    # --- サブスキル（不明ならデフォルトへフォールバック） ---
    select_subskill_with_fallback(driver, "pokemon_subskill1", sub10, DEFAULT_SUBSKILL_1)
    select_subskill_with_fallback(driver, "pokemon_subskill2", sub25, DEFAULT_SUBSKILL_2)
    select_subskill_with_fallback(driver, "pokemon_subskill3", sub50, DEFAULT_SUBSKILL_3)

    # --- 性格 ---
    select_personality(driver, record["personality"])

    # --- 進化回数 ---
    select_evolution_count(driver, record["pokemon"])

    # --- 各 Lv でチェック蓄積（高い順：70→60→30） ---
    for lv in LEVELS_TO_CHECK:  # [70, 60, 30]
        set_level(driver, lv)
        click_check_button(driver)
        sleep(9)

    # --- 残りの進化系があれば順次変更して再チェック ---
    for loop_name in poke_name_list[1:]:
        if not pokemon_select(driver, loop_name):
            continue
        for lv in LEVELS_TO_CHECK:
            set_level(driver, lv)
            click_check_button(driver)
            sleep(9)

    # --- 蓄積されたテーブルを1回パース ---
    results = parse_checker_table(driver)

    # --- フォームリセット ---
    reset_form(driver)

    print(f"個体値取得結果: {results}")
    return results
