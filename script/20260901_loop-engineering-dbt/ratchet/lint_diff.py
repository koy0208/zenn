"""差分リンタ ─ 「症状を黙らせる」修正パターンを決定論的に検出する。

LLM の判断に頼らず、git diff の追加行だけを見て機械的に弾く。
どのパターンも「常に間違い」ではないので、正当な理由があるなら
その行に `loop-ok: <理由>` と書けば通る。黙って通ることはできない、
という形にして、ショートカットを《記録された判断》に変えるのが狙い。

終了コード:
  0 = 該当なし
  3 = 要justification（人間かエージェントが理由を書く必要がある）
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = "jaffle-shop/models"

RULES = [
    (
        re.compile(r"\bselect\s+distinct\b|\bdistinct\s+on\b", re.I),
        "distinct",
        "行が増えているなら join が壊れている。distinct は原因を隠したまま行数だけ合わせる。",
    ),
    (
        re.compile(r"\bqualify\b", re.I),
        "qualify",
        "row_number() で 1 行に絞ると、残った行以外の値が捨てられる。"
        "主キーは一意になるが、残る値は order by 次第で任意になる。",
    ),
    (
        re.compile(r"\bany_value\s*\(", re.I),
        "any_value",
        "その列が集計粒度で一意でないなら、返るのは「たまたま最初に見つかった行」の値。"
        "一意なら、そもそもなぜ集計しているのかを問い直す。",
    ),
    (
        re.compile(r"\binner\s+join\b", re.I),
        "inner join",
        "NULL を消すために inner join に変えると行が消える。粒度が変わっていないか確認する。",
    ),
    (
        re.compile(r"\bwhere\b[^\n]*\bis\s+not\s+null\b", re.I),
        "where is not null",
        "テストで落ちた行を where で除外していないか。除外は修正ではない。",
    ),
]

ESCAPE = re.compile(r"loop-ok\s*:", re.I)


def added_lines(diff_range):
    """git diff の追加行を (path, lineno, text) で返す。"""
    cmd = ["git", "-C", str(ROOT), "diff", "-U0"]
    if diff_range:
        cmd.append(diff_range)
    cmd += ["--", TARGET]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout

    path, lineno = None, 0
    for raw in out.splitlines():
        if raw.startswith("+++ b/"):
            path = raw[6:]
        elif raw.startswith("@@"):
            m = re.search(r"\+(\d+)", raw)
            lineno = int(m.group(1)) if m else 0
        elif raw.startswith("+") and not raw.startswith("+++"):
            yield path, lineno, raw[1:]
            lineno += 1


def main():
    diff_range = sys.argv[1] if len(sys.argv) > 1 else None
    hits = []

    for path, lineno, text in added_lines(diff_range):
        stripped = re.sub(r"--.*$", "", text)  # SQL コメントは対象外
        if ESCAPE.search(text):
            continue
        for pattern, name, why in RULES:
            if pattern.search(stripped):
                hits.append((path, lineno, name, why, text.strip()))
                break

    if not hits:
        print("lint: 該当なし")
        return 0

    print("=== LINT: 要justification ===")
    for path, lineno, name, why, text in hits:
        print(f"\n  {path}:{lineno}  [{name}]")
        print(f"    {text}")
        print(f"    → {why}")

    print(
        "\n正当な理由があるなら、その行に `loop-ok: <理由>` を書いて再実行する。\n"
        "理由を書けないなら、それは症状を黙らせているだけ。"
    )
    return 3


if __name__ == "__main__":
    sys.exit(main())
