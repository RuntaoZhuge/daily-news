#!/usr/bin/env python3
"""Rebuild index.html, archive.html and feed.json from the daily issue files.

Usage:  python3 build.py
Each issue is a self-contained HTML file named YYYY-MM-DD.html in this folder.
No third-party dependencies.
"""

import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
ISSUE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\.html$")

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
MONTHS_EN = {
    1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN",
    7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC",
}


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def read_issue(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    d = date.fromisoformat(path.stem)

    def meta(name: str) -> str:
        m = re.search(
            r'<meta\s+name="dn:%s"\s+content="([^"]*)"' % name, text, re.I
        )
        return html.unescape(m.group(1)).strip() if m else ""

    title_m = re.search(r"<h1>(.*?)</h1>", text, re.S)
    title = strip_tags(title_m.group(1)) if title_m else "每日简报"

    focus: list[str] = []
    block = re.search(r'class="focus".*?<ol>(.*?)</ol>', text, re.S)
    if block:
        focus = [strip_tags(x) for x in re.findall(r"<li>(.*?)</li>", block.group(1), re.S)]

    return {
        "date": d.isoformat(),
        "issue": meta("issue"),
        "summary": meta("summary"),
        "title": title,
        "focus": focus,
        "file": path.name,
    }


def load_issues() -> list[dict]:
    issues = []
    for p in ROOT.iterdir():
        if p.is_file() and ISSUE_RE.match(p.name):
            issues.append(read_issue(p))
    issues.sort(key=lambda i: i["date"], reverse=True)
    return issues


def human_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.year} 年 {d.month} 月 {d.day} 日 · {WEEKDAYS[d.weekday()]}"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


HEAD = """<!DOCTYPE html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<div class="wrap">
"""


def render_index(issues: list[dict]) -> str:
    latest = issues[0]
    cards = []
    for it in issues[1:7]:
        first = it["focus"][0] if it["focus"] else it["summary"]
        cards.append(
            f"""      <a class="card" href="./{esc(it['file'])}">
        <div class="card-date">{it['date']}<span class="card-issue">第 {esc(it['issue'])} 期</span></div>
        <div class="card-lead">{esc(first[:58])}{'…' if len(first) > 58 else ''}</div>
      </a>"""
        )

    focus_html = "\n".join(f"        <li>{esc(x)}</li>" for x in latest["focus"][:3])

    if cards:
        recent_block = (
            '  <h2 class="sec-h">往期</h2>\n  <div class="grid">\n'
            + "\n".join(cards)
            + '\n  </div>\n'
            + f'  <p class="more"><a href="./archive.html">查看全部 {len(issues)} 期 →</a></p>\n'
        )
    else:
        recent_block = ""

    body = f"""  <section class="masthead">
    <div class="kicker">Daily Briefing · Melbourne</div>
    <h1>世界、中国、澳洲与墨尔本<br>每日简报</h1>
    <p class="sub">世界主要事件 · 中国政治 · 澳洲新闻 · 墨尔本新闻 · 科技与 AI · 世界经济</p>
    <p class="meta">每天 07:30（墨尔本时间）自动更新 · 共 <b>{len(issues)}</b> 期 · <a href="./archive.html">归档</a> · <a href="https://github.com/RuntaoZhuge/daily-news" target="_blank" rel="noopener">GitHub</a></p>
  </section>

  <a class="latest" href="./{esc(latest['file'])}">
    <div class="latest-tag">最新一期</div>
    <div class="latest-date">{human_date(latest['date'])}<span class="latest-issue">第 {esc(latest['issue'])} 期</span></div>
    <ol class="latest-focus">
{focus_html}
    </ol>
    <div class="latest-cta">阅读全文 →</div>
  </a>

{recent_block}"""
    return HEAD.format(
        title="每日简报 · 世界、中国、澳洲与墨尔本",
        desc="每天 07:30 更新的中文新闻简报：世界主要事件、中国政治、澳洲与墨尔本本地新闻、科技与 AI、世界经济。",
    ) + body + FOOT


def render_archive(issues: list[dict]) -> str:
    groups: dict[str, list[dict]] = {}
    for it in issues:
        groups.setdefault(it["date"][:7], []).append(it)

    out = []
    for ym in sorted(groups, reverse=True):
        y, m = ym.split("-")
        out.append(f'  <h2 class="sec-h">{y} 年 {int(m)} 月</h2>\n  <ul class="list">')
        for it in groups[ym]:
            first = it["focus"][0] if it["focus"] else it["summary"]
            out.append(
                f'    <li><a href="./{esc(it["file"])}">'
                f'<span class="d">{it["date"]}</span>'
                f'<span class="t">{esc(first[:70])}{"…" if len(first) > 70 else ""}</span></a></li>'
            )
        out.append("  </ul>")

    body = f"""  <section class="masthead">
    <div class="kicker">Archive</div>
    <h1>简报归档</h1>
    <p class="meta">共 <b>{len(issues)}</b> 期 · <a href="./index.html">← 返回首页</a></p>
  </section>
{chr(10).join(out)}
"""
    return HEAD.format(title="简报归档 · 每日简报", desc="全部往期简报归档。") + body + FOOT


FOOT = """  <footer>
    <p>每天 07:30（澳大利亚墨尔本时间）自动生成，内容基于公开报道整理，链接指向原始来源。</p>
    <p>仅供信息参考，不构成投资建议。 · <a href="https://github.com/RuntaoZhuge/daily-news">源文件与构建脚本</a></p>
  </footer>
</div>
</body>
</html>
"""


def main() -> None:
    issues = load_issues()
    if not issues:
        raise SystemExit("no issues found: expected YYYY-MM-DD.html files")

    (ROOT / "index.html").write_text(render_index(issues), encoding="utf-8")
    (ROOT / "archive.html").write_text(render_archive(issues), encoding="utf-8")
    (ROOT / "feed.json").write_text(
        json.dumps(
            [
                {
                    "date": i["date"],
                    "issue": i["issue"],
                    "title": i["title"],
                    "summary": i["summary"],
                    "focus": i["focus"],
                    "url": i["file"],
                }
                for i in issues
            ],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"built index.html, archive.html, feed.json from {len(issues)} issue(s)")


if __name__ == "__main__":
    main()
