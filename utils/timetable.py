"""
I generated this with chatgpt and im not ashamed of that
"""

import re
import time
from collections import defaultdict
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import imgkit

config = imgkit.config(wkhtmltoimage=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe")


def fetch_timetable_rows():
    url = "https://studentssp.setu.ie/timetables/StudentGroupTT.aspx"
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # select dropdowns (same values you used)
    Select(driver.find_element("id", "cboSchool")).select_by_value("SS")
    Select(driver.find_element("id", "CboDept")).select_by_value("548715F70874B2B1561DDC98FE61E5C0")
    Select(driver.find_element("id", "CboPOS")).select_by_value("85EA4CF769354ECAD9F18363EC561526")
    Select(driver.find_element("id", "CboStudParentGrp")).select_by_value("kcmsc_b1-W_W3/W4")

    driver.find_element("id", "BtnRetrieve").click()
    time.sleep(2)  # wait for the timetable to appear

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    timetable_div = soup.find("div", {"id": "divTT"})
    if not timetable_div:
        raise RuntimeError("Could not find timetable on page")

    # the timetable table is usually the second table in that div (as you used)
    tables = timetable_div.find_all("table")
    if len(tables) < 2:
        raise RuntimeError("Unexpected timetable HTML structure")
    table = tables[1]

    rows = []
    for tr in table.find_all("tr"):
        cols = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
        if any(cols):
            rows.append(cols)
    return rows


def pretty_group_label(group_info: str, subject_text: str):
    """Return a compact label for group_info:
       - 'W3', 'W4', 'W3/W4' for those cases
       - 'P5' (or 'P') for physics lab markings (various formats)
       - otherwise a compact last token for display
    """
    gi = (group_info or "").strip()

    # shared lectures
    if "W_W3/W4" in gi or "W_W3/W4" in gi.replace(" ", ""):
        return "W3/W4"

    # explicit W_W3 or W_W4
    m = re.search(r"W_W(\d+)", gi)
    if m:
        return "W" + m.group(1)

    # explicit W_Pxx pattern (e.g. W_P5)
    m = re.search(r"W[_-]?P(\d+)", gi, re.I)
    if m:
        return "P" + m.group(1)

    # explicit P# somewhere
    m = re.search(r"\bP(\d+)\b", gi, re.I)
    if m:
        return "P" + m.group(1)

    # patterns like -W05 or _W05 (site sometimes uses W05 for labs) — only treat as lab
    # if subject mentions physics (avoid confusing regular W3/W4)
    m = re.search(r"[-_]W0?(\d{1,2})\b", gi)
    if m and re.search(r"physic", subject_text, re.I):
        return "P" + m.group(1)  # treat as a physics-lab code

    # fallback: very compact representation (last token after dash/underscore)
    if "-" in gi:
        return gi.split("-")[-1]
    if "_" in gi:
        return gi.split("_")[-1]
    return gi or ""


def is_lab_label(label: str):
    """Return True if label indicates a physics lab (starts with 'P')."""
    return bool(label) and label.upper().startswith("P")


def parse_rows_to_timetable(rows, group):
    """
    rows: list of columns lists as returned from fetch_timetable_rows()
    group: "W3" or "W4" (string)
    returns: timetable dict: {day: {time: [entry, ...]}}
    where entry is dict {subject, room, staff, label}
    """
    timetable = defaultdict(lambda: defaultdict(list))
    current_day = None
    for cols in rows:
        # detect day rows: often a single column like "Wednesday"
        if len(cols) == 1 and cols[0] and cols[0].isalpha():
            current_day = cols[0]
            continue

        # many pages have these columns:
        # [time, subject, group_info, type, week, staff, room]
        if len(cols) >= 2 and current_day:
            time_str = cols[0]
            subject = cols[1]
            # try to pick group_info from 3rd column if present (safe fallback to "")
            group_info = cols[2] if len(cols) > 2 else ""
            # staff and room often are last two columns; take safe defaults
            staff = cols[-2] if len(cols) >= 3 else ""
            room = cols[-1] if len(cols) >= 1 else ""

            # derive compact label (W3/W4 or P# etc)
            label = pretty_group_label(group_info, subject)

            # decide inclusion logic:
            # 1) labs (label starts with P) -> always include (in both W3 & W4 outputs)
            # 2) shared (W3/W4) -> include in both
            # 3) group-specific (W3 or W4) -> include only in matching group
            include = False
            if is_lab_label(label):
                include = True
            elif label == "W3/W4":
                include = True
            elif ("W_" + group) in (group_info or "") or label.upper() == ("W" + group[-1]):  # fallback checks
                include = True
            else:
                include = False

            if include:
                entry = {
                    "subject": subject,
                    "room": room,
                    "staff": staff,
                    "label": label,
                    "raw_group": group_info,
                }
                timetable[current_day][time_str].append(entry)

    # convert defaultdict to normal dict for usability
    return {d: dict(timetable[d]) for d in timetable}


def get_sorted_times(timetable_dicts):
    """Collect all times across both timetables and sort ascending (HH:MM)."""
    times_set = set()
    for td in timetable_dicts:
        for day, slots in td.items():
            times_set.update(slots.keys())

    # parse HH:MM into minutes for correct ordering
    def to_minutes(t):
        try:
            h, m = map(int, t.split(":"))
            return h * 60 + m
        except Exception:
            return 9999

    return sorted(times_set, key=to_minutes)


def subject_css_class(subject, label):
    s = subject.lower()
    if is_lab_label(label):
        return "lab"
    if "math" in s or "discrete" in s:
        return "math"
    if "physics" in s:
        return "physics"
    if "website" in s or "web" in s or "html" in s:
        return "webdev"
    if "program" in s or "coding" in s:
        return "programming"
    if "system" in s:
        return "systems"
    return "default"


def timetable_to_html(timetable, group_name, all_times, days_order=None):
    if days_order is None:
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    html = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <style>
      body {{ font-family: Arial, sans-serif; background:#f6f7fb; padding:20px; }}
      h2 {{ text-align:center; margin-bottom:8px; }}
      table {{ border-collapse: collapse; width:100%; table-layout: fixed; }}
      th, td {{ border:1px solid #e0e0e0; padding:6px; vertical-align:top; }}
      th {{ background:#222; color:white; padding:10px; font-size:14px; }}
      td {{ height:110px; overflow:hidden; }}
      .cell {{ display:flex; flex-direction:column; gap:6px; }}
      .entry {{ border-radius:8px; padding:6px; font-size:12px; box-shadow: 0 1px 0 rgba(0,0,0,0.04); }}
      .entry .meta {{ font-size:10px; opacity:0.85; margin-top:4px; }}
      .math {{ background:#a78bfa; color:white; }}
      .physics {{ background:#f97316; color:white; }}
      .webdev {{ background:#38bdf8; color:white; }}
      .programming {{ background:#60a5fa; color:white; }}
      .systems {{ background:#34d399; color:white; }}
      .industry {{ background:#facc15; color:black; }}
      .lab {{ background:#ef4444; color:white; }}
      .default {{ background:#e6eef8; color:#0b2545; }}
      .small-label {{ font-weight:600; margin-right:6px; }}
      .meta-row {{ font-size:11px; opacity:0.9; }}
    </style>
    </head>
    <body>
      <h2>Timetable — {group_name}</h2>
      <table>
        <tr>
          <th style="width:90px;">Time</th>
    """
    for d in days_order:
        html += f"<th>{d}</th>"
    html += "</tr>"

    for t in all_times:
        html += f"<tr><td><b>{t}</b></td>"
        for d in days_order:
            entries = timetable.get(d, {}).get(t, [])
            if not entries:
                html += "<td></td>"
            else:
                html += "<td><div class='cell'>"
                for e in entries:
                    css = subject_css_class(e["subject"], e["label"])
                    label_txt = e["label"] if e["label"] else ""
                    # show label as "P5" or "W3/W4" or "W3"/"W4"
                    meta_parts = []
                    if label_txt:
                        meta_parts.append(label_txt)
                    if e.get("room"):
                        meta_parts.append(e["room"])
                    if e.get("staff"):
                        meta_parts.append(e["staff"])
                    meta = " • ".join([p for p in meta_parts if p])
                    html += "<div class='entry {cls}'>".format(cls=css)
                    html += f"<div class='title'>{e['subject']}</div>"
                    if meta:
                        html += f"<div class='meta'>{meta}</div>"
                    html += "</div>"
                html += "</div></td>"
        html += "</tr>"

    html += "</table></body></html>"
    return html


def generate_timetable(group: str or list):
    if isinstance(group, list):
        data = []
        for g in group:
            rows = fetch_timetable_rows()
            timetable = parse_rows_to_timetable(rows, g)
            times = get_sorted_times([timetable])
            html = timetable_to_html(timetable, f"Group {g}", times)
            data.append(imgkit.from_string(html, False, config=config))
        return data
    else:
        rows = fetch_timetable_rows()
        timetable = parse_rows_to_timetable(rows, group)
        times = get_sorted_times([timetable])
        html = timetable_to_html(timetable, f"Group {group}", times)
        return imgkit.from_string(html, False, config=config)

