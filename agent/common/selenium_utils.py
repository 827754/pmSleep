"""
Selenium WebDriver の共通ユーティリティ。
ドライバ作成・広告クローズ等、サイトに依存しない操作をまとめる。
"""

from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def create_driver(headless=True):
    """Chrome WebDriver を作成して返す。

    Args:
        headless: True の場合バックグラウンド（非表示）で起動する。

    Returns:
        webdriver.Chrome インスタンス。
    """
    options = Options()
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


def close_ad_if_exists(driver):
    """広告オーバーレイ（close-overlay）があれば閉じる。

    ない場合は例外を握りつぶして静かに復帰する。
    スクレイピング途中の広告誤判定を防ぐため、各クリック直前に呼ぶことを想定している。
    """
    try:
        close_button = driver.find_element(By.ID, "close-overlay")
        close_button.click()
        print("広告を閉じました")
        sleep(5)  # 広告アニメーションや再描写を待つ
    except Exception:
        # 広告なし → 何もしない
        pass
