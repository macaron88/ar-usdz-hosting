#!/usr/bin/env python3
"""VADO共通 時間認識モジュール（日本標準時 Asia/Tokyo）。

用途: Claude Code の SessionStart / UserPromptSubmit Hook から呼ぶ。
      どのAI社員（バトー、ミルカ等）でも同じ1本を使う。外部サービス・追加パッケージ不要（標準ライブラリのみ）。

使い方:
  now_jst.py hook SessionStart      -> Hook用JSON（additionalContext）を出力
  now_jst.py hook UserPromptSubmit  -> Hook用JSON（additionalContext）を出力
  now_jst.py text                   -> 人間が読む1ブロックを出力（テスト・他ツール用）

方針:
  * 時刻は実行環境のシステム時計(UTC)から取得し、JSTへ変換する。推測しない。
  * 時間帯(朝/昼/夕方/夜)は「判断の目安」であり、業務終了の根拠にしない。
  * このスクリプトは「業務終了」を判定しない。判定材料も出さない。
"""
import json
import sys
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
    JST = ZoneInfo("Asia/Tokyo")
except Exception:  # tzdata が無い環境用の保険（日本は夏時間なし＝UTC+9固定）
    JST = timezone(timedelta(hours=9), "JST")

WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]


def time_band(hour: int) -> str:
    # 初期値（府川さんの確認後に調整可）。あくまで優先順位を見直す目安。
    if 5 <= hour < 11:
        return "朝（5:00〜10:59）"
    if 11 <= hour < 16:
        return "昼（11:00〜15:59）"
    if 16 <= hour < 19:
        return "夕方（16:00〜18:59）"
    return "夜・早朝（19:00〜4:59）"


def build_text() -> str:
    utc = datetime.now(timezone.utc)
    jst = utc.astimezone(JST)
    return (
        "【現在日時（日本標準時・実行環境の時計から取得）】\n"
        f"{jst:%Y年%m月%d日}（{WEEKDAYS[jst.weekday()]}曜日）{jst:%H:%M} JST\n"
        f"時間帯の目安: {time_band(jst.hour)}\n"
        f"（照合用 UTC: {utc:%Y-%m-%d %H:%M}Z）\n"
        "【時間認識ルール】\n"
        "- 日付・曜日・時刻はこの値を使い、推測しない。\n"
        "- 本日の予定はGoogleカレンダーで確認し、締切・残務を時間軸で優先順位づけする。\n"
        "- 日付が変わったことを理由に、未完了の業務を完了扱いしない。\n"
        "- バトー自身の作業完了と、府川さんの業務終了は別。時刻だけで「今日は終了」と判断しない。\n"
        "  業務終了は府川さんが伝えたときだけ扱い、その場合に未完了業務と翌日の引き継ぎを整理する。"
    )


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "text"
    text = build_text()
    if mode == "hook":
        event = sys.argv[2] if len(sys.argv) > 2 else "UserPromptSubmit"
        json.dump(
            {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}},
            sys.stdout,
            ensure_ascii=False,
        )
    else:
        print(text)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)  # Hookの失敗で会話を止めない
