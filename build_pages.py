#!/usr/bin/env python3
"""Build index.html (today) and yesterday.html from the two newest briefs in briefs/.

Usage: python3 build_pages.py   (run from the repo root)
Idempotent: safe to re-run any time.
"""
import re
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BRIEFS = ROOT / "briefs"

NAV_MARK = "<!--brief-nav-->"

def nav_html(current, today_label, yest_label):
    def link(href, label, active):
        if active:
            return ('<span style="padding:6px 14px;border-radius:999px;'
                    'background:var(--accent,#0f4c5c);color:#fff;font-weight:600;">%s</span>' % label)
        return ('<a href="%s" style="padding:6px 14px;border-radius:999px;'
                'background:var(--chipbg,#f0efec);color:var(--ink,#0b0b0b);'
                'text-decoration:none;font-weight:600;">%s</a>' % (href, label))
    return (
        NAV_MARK + '<nav style="max-width:960px;margin:0 auto;padding:14px 16px 0;'
        'display:flex;gap:10px;align-items:center;font-size:14px;'
        'font-family:system-ui,-apple-system,sans-serif;">'
        + link("index.html", "Today &middot; " + today_label, current == "today")
        + link("yesterday.html", "Yesterday &middot; " + yest_label, current == "yesterday")
        + "</nav>"
    )

def label_for(path):
    d = datetime.date.fromisoformat(path.stem.replace("brief-", ""))
    return d.strftime("%a %-d %b")

def inject(src, out, current, today_label, yest_label):
    html = src.read_text(encoding="utf-8")
    html = re.sub(re.escape(NAV_MARK) + r".*?</nav>", "", html, flags=re.S)
    html = re.sub(r"(<body[^>]*>)", r"\1" + nav_html(current, today_label, yest_label),
                  html, count=1)
    out.write_text(html, encoding="utf-8")

def main():
    briefs = sorted(BRIEFS.glob("brief-????-??-??.html"))
    if not briefs:
        raise SystemExit("no briefs/brief-YYYY-MM-DD.html files found")
    keep = briefs[-2:]
    for old in briefs[:-2]:
        old.unlink()
    today = keep[-1]
    yest = keep[0] if len(keep) > 1 else keep[-1]
    t_label, y_label = label_for(today), label_for(yest)
    inject(today, ROOT / "index.html", "today", t_label, y_label)
    inject(yest, ROOT / "yesterday.html", "yesterday", t_label, y_label)
    print("built index.html (%s) and yesterday.html (%s)" % (t_label, y_label))

if __name__ == "__main__":
    main()
