"""
だいふく氏サイト（pokemonsleepdaifuku.com）での共通UI操作。
/checker/ と /checker/expected/ 双方で使うポケモン選択・食材選択等をまとめる。
"""

from time import sleep
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException

from common.selenium_utils import close_ad_if_exists
from common.poke_utils import get_pokemon_evolution_cnt


# ---------------------------------------------------------------------------
# ページ遷移
# ---------------------------------------------------------------------------
def navigate_to(driver, url):
    """指定URLにアクセスする。"""
    driver.get(url)


# ---------------------------------------------------------------------------
# ポケモン選択（select2 ドロップダウン）
# ---------------------------------------------------------------------------
def pokemon_select(driver, pokemon_name):
    """ポケモン名を select2 ドロップダウンで選択する。

    - 括弧付きポケモン（例：ピカチュウ(キャプテン)）→ 完全一致で探す
    - 通常ポケモン → 部分一致だが、括弧付き候補はスキップ（別姿を避ける）

    Returns:
        bool: 選択成功なら True。
    """
    poke_dropdown = driver.find_element(By.ID, "pokemonNameSelect")
    dropdown_span = driver.find_element(
        By.XPATH, "//span[@aria-labelledby='select2-pokemonNameSelect-container']"
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", poke_dropdown)
    close_ad_if_exists(driver)
    dropdown_span.click()
    sleep(1)
    print(f"選択対象ポケモン: {pokemon_name}")

    try:
        list_items = driver.find_elements(
            By.XPATH, "//ul[@class='select2-results__options']//li"
        )
        target = None
        for option in list_items:
            if "（" in pokemon_name and "）" in pokemon_name:
                if pokemon_name in option.text:
                    target = option
                    break
            else:
                if pokemon_name in option.text:
                    if "（" in option.text and "）" in option.text:
                        continue
                    target = option
                    break

        if target:
            selected_text = target.text
            close_ad_if_exists(driver)
            target.click()
            print(f"選択しました: {selected_text}")
            sleep(1)
            return True
        else:
            print(f"{pokemon_name} がリストに見つかりませんでした。")
            # ドロップダウンを閉じておく
            dropdown_span.click()
            return False

    except NoSuchElementException:
        return False


# ---------------------------------------------------------------------------
# 食材選択（select2 ドロップダウン）
# ---------------------------------------------------------------------------
def select_ingredient(driver, ingredient_name, element_id):
    """食材ドロップダウンで指定名を選択する。

    ingredient_name がリストにない場合は False を返し、
    呼び出し側で continue / スキップ判定を行うことを想定している。
    """
    pokemon_ingredient = driver.find_element(By.NAME, "pokemon_ingredient1")
    driver.execute_script("arguments[0].scrollIntoView(true);", pokemon_ingredient)
    sleep(1)

    dropdown_span = driver.find_element(
        By.XPATH, f"//span[contains(@aria-labelledby, '{element_id}')]"
    )
    close_ad_if_exists(driver)
    dropdown_span.click()
    sleep(1)

    list_items = driver.find_elements(
        By.XPATH, "//ul[@class='select2-results__options']//li"
    )

    ingredient_option = None
    for option in list_items:
        if ingredient_name in option.text:
            ingredient_option = option
            break

    if ingredient_option:
        close_ad_if_exists(driver)
        ingredient_option.click()
        print(f"選択しました: {ingredient_name}")
        return True
    else:
        print(f"{ingredient_name} がリストに見つかりませんでした。")
        return False


# ---------------------------------------------------------------------------
# サブスキル選択（2パターン）
# ---------------------------------------------------------------------------
def select_subskill_by_visible_text(driver, element_name, skill_name):
    """select_by_visible_text でサブスキルを選ぶ。（期待値ページ用）"""
    dropdown = driver.find_element(By.NAME, element_name)
    sleep(1)
    select = Select(dropdown)
    select.select_by_visible_text(skill_name)


def select_subskill_with_fallback(driver, element_name, skill_name, default_skill):
    """サブスキルを選ぶ。不明な場合は default_skill にフォールバックする。（個体値ページ用）

    Returns:
        str: 最終的に選択されたスキル名。
    """
    from common.poke_utils import replace_unknown

    dropdown = driver.find_element(By.NAME, element_name)
    sleep(1)
    select = Select(dropdown)
    final_skill = replace_unknown(skill_name, default_skill)
    select.select_by_visible_text(final_skill)
    return final_skill


# ---------------------------------------------------------------------------
# 性格選択
# ---------------------------------------------------------------------------
def select_personality(driver, personality):
    """性格を部分一致で探して選択する。

    Returns:
        str or None: 選択した完全名。見つからなければ None。
    """
    dropdown = driver.find_element(By.NAME, "pokemon_personality")
    sleep(1)
    select = Select(dropdown)
    for option in select.options:
        if personality in option.text:
            select.select_by_visible_text(option.text)
            return option.text
    return None


# ---------------------------------------------------------------------------
# MainLv 選択（ラジオボタン）
# ---------------------------------------------------------------------------
def select_main_lv(driver, main_lv):
    """MainスキルLvのラジオボタンを選択する。"""
    print(f"MainLv: {main_lv}")
    main_btn = driver.find_element(By.XPATH, f"//label[@for='{main_lv}']")
    driver.execute_script("arguments[0].scrollIntoView(true);", main_btn)
    close_ad_if_exists(driver)
    main_btn.click()


# ---------------------------------------------------------------------------
# 進化回数選択（ラジオボタン）
# ---------------------------------------------------------------------------
def select_evolution_count(driver, pokemon_name):
    """進化回数のラジオボタンを選ぶ。

    ストリンダー系・限定衣装ポケモンの特殊処理を含む。

    Returns:
        int: 選択した進化回数。
    """
    special = ["ホリデー", "ハロウィン", "キャプテン"]

    if "ストリンダー" in pokemon_name:
        evo_cnt = int(get_pokemon_evolution_cnt(pokemon_name))
    elif all(x not in pokemon_name for x in special):
        evo_cnt = int(get_pokemon_evolution_cnt(re.sub(r"（.*$", "", pokemon_name)))
    else:
        evo_cnt = 0

    evo_btn = driver.find_element(By.XPATH, f"//label[@for='num_evolved{evo_cnt}']")
    driver.execute_script("arguments[0].scrollIntoView(true);", evo_btn)
    close_ad_if_exists(driver)
    evo_btn.click()
    return evo_cnt


# ---------------------------------------------------------------------------
# レベル変更（/checker/ と /checker/expected/ 双方で共通）
# ---------------------------------------------------------------------------
def set_level(driver, level):
    """レベル入力欄 (levelDisplay) を直接変更し、input/change イベントを発火させる。

    個体値ページではスライダーがインデックス制御（0=30,1=50,2=60,3=70）のため、
    スライダー操作を避けてテキストボックスのみでレベルを変更する。
    """
    level_input = driver.find_element(By.ID, "levelDisplay")
    driver.execute_script(
        "arguments[0].value = arguments[1];"
        "arguments[0].dispatchEvent(new Event('input',  { bubbles: true }));"
        "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
        level_input, str(level)
    )
    sleep(0.5)


# ---------------------------------------------------------------------------
# チェックボタン・リセット
# ---------------------------------------------------------------------------
def click_check_button(driver):
    """チェックボタン（submitButton class）をクリックする。"""
    check_btn = driver.find_element(By.CLASS_NAME, "submitButton")
    driver.execute_script("arguments[0].scrollIntoView(true);", check_btn)
    close_ad_if_exists(driver)
    check_btn.click()


def reset_form(driver):
    """フォームをリセットする。"""
    reset_btn = driver.find_element(By.ID, "resetButton")
    sleep(5)
    close_ad_if_exists(driver)
    driver.execute_script("arguments[0].click();", reset_btn)
