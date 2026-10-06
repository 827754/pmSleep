"""
だいふくスクレイピングのメインエントリポイント。

個体値ページ（/checker/）と期待値ページ（/checker/expected/）を統合して、
新しい dc 形式のデータを構築・保存する。

処理フロー:
  1. {uid}.json を読み込み
  2. 削除フラグ処理（既存コードと同等：最新10件のみ残す）
  3. 処理順ソート（dc未作成優先 → upd 古い順）
  4. 日次上限（DAILY_LIMIT）で絞り込み
  5. 各レコードを個体値→期待値の順で取得
  6. dc 形式に統合して record["dc"] に保存
  7. JSON を上書き保存

既存の record["new_d"] はそのまま残す（互換性維持）。
"""

import json
import os
from datetime import datetime
from time import sleep

from config import UIDS, DAILY_LIMIT, HEADLESS_DEFAULT, DATA_DIR
from common.selenium_utils import create_driver
from sites.daifuku_checker import fetch_individual_rates
from sites.daifuku_expected import fetch_expected_values


# ---------------------------------------------------------------------------
# JSON入出力
# ---------------------------------------------------------------------------
def load_records(uid):
    """{uid}.json を読み込んで Python リストを返す。

    ファイルは DATA_DIR に配置されていることを想定。
    utf-8-sig を使用して、BOM 付き/なしの両方に対応する。
    """
    path = os.path.join(DATA_DIR, f"{uid}.json")
    if not os.path.exists(path):
        print(f"[WARN] {path} が見つかりません。スキップします。")
        return []
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_records(uid, records):
    """レコードリストを {uid}.json に上書き保存する。

    ファイルは DATA_DIR に配置されていることを想定。
    BOM なし utf-8 で出力する。
    """
    path = os.path.join(DATA_DIR, f"{uid}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False)


# ---------------------------------------------------------------------------
# 削除フラグ処理（既存コードと同等のロジック）
# ---------------------------------------------------------------------------
def filter_deleted(records):
    """削除フラグが立っているレコードを最新10件のみ残してフィルタリングする。

    元の順番を保持しつつ、削除以外のレコードと最新削除10件を残す。
    """
    deleted = [r for r in records if r.get("flag") == "削除"]
    deleted.sort(
        key=lambda x: datetime.strptime(x["date"], "%y年%m月%d日"),
        reverse=True,
    )
    latest_deleted = deleted[:10]

    remaining = []
    for r in records:
        if r.get("flag") != "削除" or r in latest_deleted:
            remaining.append(r)
    return remaining


# ---------------------------------------------------------------------------
# 処理順ソート
# ---------------------------------------------------------------------------
def sort_for_processing(records):
    """レコードを処理順に並べ替える。

    優先順位:
      1. dc が未作成のものを最優先
      2. upd（更新日 yymmdd）が古いものを優先
      3. upd が空（未調査）のものは最も古い扱い
    """
    def sort_key(record):
        has_dc = bool(record.get("dc"))
        upd = record.get("upd", "")
        upd_norm = upd if upd else "000000"
        # has_dc=False（0）が先に来るように
        return (has_dc, upd_norm)

    return sorted(records, key=sort_key)


# ---------------------------------------------------------------------------
# dc 構築
# ---------------------------------------------------------------------------
def build_dc(individual_results, expected_results):
    """個体値結果と期待値結果を統合して dc 形式のリストを構築する。

    individual_results: list[dict]
        例: [{"name": "カメックス", "Lv": "60", "rate": "A：56.81%", "forte": "⑤"}, ...]
    expected_results: dict
        例: {"カメックス": {"name": "カメックス", "Lvs": [
                {"Lv": "30", "f": [...], "s": [...], "be": "..."},
                {"Lv": "60", ...},
                {"Lv": "70", ...},
            ]}}

    Returns:
        list[dict]: dc 形式のデータリスト。
    """
    dc = []
    for name, exp_data in expected_results.items():
        dc.append({
            "name": name,
            "forte": "",
            "Lvs": exp_data["Lvs"],  # Lv 昇順に既に並んでいる
        })

    # 個体値結果から rate / forte を補完
    for ind in individual_results:
        name = ind.get("name")
        lv = ind.get("Lv")
        rate = ind.get("rate")
        forte = ind.get("forte")
        for entry in dc:
            if entry["name"] == name:
                entry["forte"] = forte
                for lv_entry in entry["Lvs"]:
                    if lv_entry.get("Lv") == lv:
                        lv_entry["rate"] = rate
                        break
                break

    return dc


# ---------------------------------------------------------------------------
# 1レコード処理
# ---------------------------------------------------------------------------
def process_record(driver, record):
    """単一レコードを個体値→期待値の順で取得し、dc を構築して record に書き戻す。

    Returns:
        bool: 成功時 True。性格未選択・取得失敗等で False。
    """
    if record.get("personality") == "未選択":
        print("  [SKIP] 性格未選択")
        return False

    print(f"  → 個体値取得開始")
    individual_results = fetch_individual_rates(driver, record)
    if not individual_results:
        print("  [SKIP] 個体値取得失敗")
        return False

    print(f"  → 期待値取得開始")
    expected_results = fetch_expected_values(driver, record)
    if not expected_results:
        print("  [SKIP] 期待値取得失敗")
        return False

    dc = build_dc(individual_results, expected_results)
    if not dc:
        print("  [SKIP] dc 構築失敗")
        return False

    record["dc"] = json.dumps(dc, ensure_ascii=False)
    record["upd"] = datetime.now().strftime("%y%m%d")
    print(f"  [OK] dc 保存完了 ({record.get('pokemon')})")
    return True


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------
def main():
    driver = create_driver(headless=HEADLESS_DEFAULT)

    try:
        for uid in UIDS:
            print(f"\n========== UID: {uid} ==========")
            records = load_records(uid)
            if not records:
                continue

            # 削除フラグ処理
            remaining = filter_deleted(records)

            # 処理順にソート
            sorted_records = sort_for_processing(remaining)

            processed = 0
            for idx, record in enumerate(sorted_records, start=1):
                if processed >= DAILY_LIMIT:
                    print(f"[INFO] 日次上限 {DAILY_LIMIT} 件に達したため終了")
                    break

                print(f"\n[{idx}/{len(sorted_records)}] 処理開始: {record.get('pokemon')}")
                success = process_record(driver, record)
                if success:
                    processed += 1
                    # 逐次保存（既存コードと同じく、エラー時の巻き戻しを最小化）
                    save_records(uid, remaining)
                else:
                    print("  → スキップまたは失敗")

            # 最終保存
            save_records(uid, remaining)

            # 未チェック件数集計
            unchecked = sum(1 for r in remaining if not r.get("dc"))
            print(f"\n[INFO] UID {uid} 未チェック(dc未作成): {unchecked} 件")

    finally:
        driver.quit()
        print("\n[INFO] ドライバーを終了しました。")


if __name__ == "__main__":
    main()
