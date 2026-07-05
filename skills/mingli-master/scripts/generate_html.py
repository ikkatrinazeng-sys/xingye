#!/usr/bin/env python3
"""生成紫微斗数命盘 HTML 报告"""

import argparse
import json
import sys
import os

PALACE_ORDER = [
    '命宫', '兄弟宫', '夫妻宫', '子女宫', '财帛宫', '疾厄宫',
    '迁移宫', '交友宫', '官禄宫', '田宅宫', '福德宫', '父母宫'
]

# 12 宫格位置映射 (row, col) in a 4x3 grid, counterclockwise from bottom-left
# Standard ZiWei chart layout
GRID_POSITIONS = {
    # bottom row left to right: 寅卯辰巳
    '寅': (3, 0), '卯': (3, 1), '辰': (3, 2), '巳': (3, 3),
    # right col bottom to top: 午未申酉
    '午': (2, 3), '未': (1, 3), '申': (0, 3),  # wait, standard is different
    # Let me use standard layout
}

BRANCH_GRID = {
    '寅': (3, 0), '卯': (3, 1), '辰': (3, 2), '巳': (3, 3),
    '午': (2, 3), '未': (1, 3), '申': (0, 3), '酉': (0, 2),
    '戌': (0, 1), '亥': (0, 0), '子': (1, 0), '丑': (2, 0),
}


def build_palace_grid(palaces):
    """Build a 4x4 grid (outer ring, center is info)"""
    grid = [[None]*4 for _ in range(4)]
    for p in palaces:
        branch = p.get('earthlyBranch', '')
        pos = BRANCH_GRID.get(branch)
        if pos:
            grid[pos[0]][pos[1]] = p
    return grid


def star_html(star):
    name = star.get('name', '')
    brightness = star.get('brightness', '')
    mutagen = star.get('mutagen', '')
    cls = 'star-major'
    if star.get('type') == 'tough':
        cls = 'star-minor tough'
    elif star.get('type') == 'adjective':
        cls = 'star-adj'
    elif star.get('type') in ('soft', 'lucky'):
        cls = 'star-minor'

    m_html = ''
    if mutagen:
        color_map = {'禄': '#3f6d3a', '权': '#9a6a1f', '科': '#2f5fa5', '忌': '#b23a2b'}
        color = color_map.get(mutagen, '#7a6e5c')
        m_html = f'<span style="color:{color};font-size:0.7em;margin-left:2px;font-weight:700">[{mutagen}]</span>'

    b_html = ''
    if brightness:
        b_html = f'<span class="brightness">{brightness}</span>'

    return f'<span class="{cls}">{name}{b_html}{m_html}</span>'


def palace_cell_html(palace, is_soul=False, is_body=False):
    if not palace:
        return '<td class="palace-cell empty"></td>'

    name = palace.get('name', '')
    branch = palace.get('earthlyBranch', '')
    stem = palace.get('heavenlyStem', '')
    majors = palace.get('majorStars', [])
    minors = palace.get('minorStars', [])
    adjs = palace.get('adjectiveStars', [])
    decadal = palace.get('decadal', {}) or {}
    dec_range = decadal.get('range', [])

    badges = ''
    if is_soul:
        badges += '<span class="badge soul">命</span>'
    if is_body:
        badges += '<span class="badge body">身</span>'

    stars_html = ''
    for s in majors:
        stars_html += star_html(s) + ' '
    stars_html += '<br>'
    for s in minors:
        stars_html += star_html(s) + ' '
    if adjs:
        stars_html += '<br>'
        for s in adjs[:3]:
            stars_html += star_html(s) + ' '

    dec_html = ''
    if dec_range and len(dec_range) >= 2:
        dec_html = f'<div class="decadal">{dec_range[0]}-{dec_range[1]}</div>'

    return f'''<td class="palace-cell" data-branch="{branch}">
  <div class="palace-header">
    <span class="palace-stem-branch">{stem}{branch}</span>
    <span class="palace-name">{name}</span>
    {badges}
  </div>
  <div class="palace-stars">{stars_html}</div>
  {dec_html}
</td>'''


def generate_grid_html(chart_data):
    palaces = chart_data.get('palaces', [])
    soul_branch_raw = chart_data.get('soul_branch', '')
    body_branch_raw = chart_data.get('body_branch', '')

    branch_map = {'子': 'zi', '丑': 'chou', '寅': 'yin', '卯': 'mao', '辰': 'chen', '巳': 'si',
                  '午': 'wu', '未': 'wei', '申': 'shen', '酉': 'you', '戌': 'xu', '亥': 'hai'}
    rev_branch = {v: k for k, v in branch_map.items()}

    def get_branch_char(raw):
        for k, v in branch_map.items():
            if v.lower() in raw.lower() or k in raw:
                return k
        return raw

    soul_branch = get_branch_char(soul_branch_raw)
    body_branch = get_branch_char(body_branch_raw)

    palace_by_branch = {p.get('earthlyBranch', ''): p for p in palaces}

    rows = []
    for r in range(4):
        cells = []
        for c in range(4):
            if r in (1, 2) and c in (1, 2):
                # Center cells - info
                if r == 1 and c == 1:
                    cells.append(f'''<td class="center-cell" colspan="2" rowspan="2">
                      <div class="center-info">
                        <div class="center-stamp"><span class="stamp-zi">命</span></div>
                        <div class="center-item">{chart_data.get("five_elements_class","")} · {chart_data.get("gender","")} · {chart_data.get("hour_name","")}</div>
                        <div class="center-item">农历 {chart_data.get("lunar_date","")}</div>
                        <div class="center-item">命宫 {soul_branch} · 身宫 {body_branch}</div>
                      </div>
                    </td>''')
                elif r == 1 and c == 2:
                    continue
                elif r == 2 and c in (1, 2):
                    continue
            else:
                # Find which branch goes here
                branch = None
                for br, pos in BRANCH_GRID.items():
                    if pos == (r, c):
                        branch = br
                        break
                palace = palace_by_branch.get(branch)
                is_soul = branch == soul_branch
                is_body = branch == body_branch
                cells.append(palace_cell_html(palace, is_soul, is_body))
        rows.append('<tr>' + ''.join(cells) + '</tr>')

    return '\n'.join(rows)


def reading_cards_html(reading):
    cards = reading.get('cards', [])
    html_parts = []
    for card in cards:
        full = card.get('full', False)
        highlight = card.get('highlight', False)
        teal = card.get('teal', False)
        title = card.get('title', '')
        badge = card.get('badge', '')
        body = card.get('body', '')
        probabilities = card.get('probabilities', [])

        extra_class = ''
        if highlight:
            extra_class = 'card-highlight'
        elif teal:
            extra_class = 'card-teal'

        width_class = 'card-full' if full else 'card-half'

        prob_html = ''
        if probabilities:
            prob_html = '<div class="prob-bars">'
            for pb in probabilities:
                pct = pb.get('pct', 0)
                label = pb.get('label', '')
                prob_html += f'''<div class="prob-item">
                  <div class="prob-label">{label}</div>
                  <div class="prob-bar-bg"><div class="prob-bar-fill" style="width:{pct}%"></div></div>
                  <div class="prob-pct">{pct}%</div>
                </div>'''
            prob_html += '</div>'

        badge_html = f'<span class="card-badge">{badge}</span>' if badge else ''

        html_parts.append(f'''<div class="reading-card {width_class} {extra_class}">
          <div class="card-title">{title}{badge_html}</div>
          <div class="card-body">{body}</div>
          {prob_html}
        </div>''')

    return '\n'.join(html_parts)


def hand_reading_html(hand_reading):
    if not hand_reading:
        return ''
    items = hand_reading.get('items', [])
    if not items:
        return ''

    items_html = ''
    for item in items:
        status = item.get('status', 'match')
        status_text = item.get('status_text', '')
        resolution = item.get('resolution', '')
        title = item.get('title', '')
        body = item.get('body', '')

        status_class = 'status-match' if status == 'match' else 'status-conflict'
        res_html = f'<div class="resolution">{resolution}</div>' if resolution else ''

        items_html += f'''<div class="hand-item">
          <div class="hand-item-title">{title}</div>
          <div class="hand-item-body">{body}</div>
          <div class="hand-status {status_class}">{status_text}</div>
          {res_html}
        </div>'''

    return f'''<div class="hand-section">
      <h3 class="section-title">手相互证</h3>
      <div class="hand-grid">{items_html}</div>
    </div>'''


def calibration_html(questions):
    if not questions:
        return ''
    q_html = ''
    for q in questions:
        text = q.get('text', '')
        hint = q.get('hint', '')
        hint_html = f'<div class="cal-hint">{hint}</div>' if hint else ''
        q_html += f'<div class="cal-question"><div class="cal-text">❓ {text}</div>{hint_html}</div>'

    return f'''<div class="calibration-section">
      <h3 class="section-title">校准追问</h3>
      <div class="cal-note">回答以下问题，可将解读准确度从约70%提升至85%+</div>
      <div class="cal-questions">{q_html}</div>
    </div>'''


def generate_html(chart_data, reading_data, output_path):
    grid_html = generate_grid_html(chart_data)
    cards_html = reading_cards_html(reading_data)
    hand_html = hand_reading_html(reading_data.get('hand_reading'))
    cal_html = calibration_html(reading_data.get('calibration_questions', []))
    current_decadal = reading_data.get('current_decadal_display', '')

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>紫微斗数命盘解读 · {chart_data.get("lunar_date","")}</title>
<style>
  :root {{
    --paper: #F3ECDD;
    --paper2: #EFE6D2;
    --ink: #2B2622;
    --vermil: #C0362C;
    --vermil-d: #9E2A22;
    --gold: #A9843F;
    --gold-d: #8A6A2F;
    --line: #C9B79B;
    --muted: #7A6E5C;
    --good: #3f6d3a;
    --warn: #C0362C;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--paper); color: var(--ink);
    font-family: 'Songti SC','STSong','Noto Serif SC',serif; min-height: 100vh;
    background-image:
      radial-gradient(circle at 18% 22%,rgba(169,132,63,.10),transparent 42%),
      radial-gradient(circle at 82% 30%,rgba(192,54,44,.06),transparent 40%),
      radial-gradient(circle at 30% 78%,rgba(169,132,63,.09),transparent 45%),
      radial-gradient(circle at 72% 85%,rgba(169,132,63,.07),transparent 40%);
    background-attachment: fixed;
  }}
  .page {{ max-width: 1000px; margin: 0 auto; padding: 32px 18px 60px; }}

  /* Header · 报头 */
  .header {{ text-align: center; margin-bottom: 30px; }}
  .header-en {{ font-family: 'Times New Roman',Georgia,serif; letter-spacing: .42em; font-size: 12px; color: var(--gold); text-transform: uppercase; margin-bottom: 12px; padding-left: .42em; }}
  .header-title {{ font-size: 2.6rem; color: var(--vermil); letter-spacing: 0.28em; padding-left: .28em; font-weight: 700; text-shadow: 1px 1px 0 rgba(158,42,34,.15); }}
  .header-sub {{ color: var(--muted); margin-top: 14px; font-size: 0.85rem; letter-spacing: .3em; padding-left: .3em; }}
  .decadal-banner {{ border: 1px solid var(--gold); box-shadow: 0 0 0 2px var(--paper),0 0 0 3px var(--vermil); padding: 8px 20px; display: inline-block; margin-top: 18px; color: var(--vermil-d); font-size: 0.85rem; letter-spacing: .12em; background: var(--paper2); }}

  /* Palace Grid · 十二宫盘 */
  .grid-section {{ margin-bottom: 34px; border: 1px solid var(--vermil); box-shadow: 0 0 0 3px var(--paper),0 0 0 4px var(--gold); padding: 6px; background: var(--paper2); }}
  table.palace-grid {{ width: 100%; border-collapse: collapse; table-layout: fixed; border: 1px solid var(--gold); }}
  .palace-cell {{ border: .5px solid var(--line); background: rgba(243,236,221,.5); padding: 8px 9px; vertical-align: top; height: 108px; }}
  .palace-cell.empty {{ background: rgba(201,183,155,.12); }}
  .center-cell {{ background: var(--paper2); border: 1px solid var(--vermil); vertical-align: middle; }}
  .center-info {{ text-align: center; padding: 12px; }}
  .center-stamp {{ width: 108px; height: 108px; margin: 0 auto 14px; background: var(--vermil); border-radius: 6px; position: relative; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 0 2px var(--paper2),0 0 0 3px var(--vermil-d); background-image: radial-gradient(circle at 35% 30%,rgba(255,255,255,.14),transparent 45%),radial-gradient(circle at 70% 75%,rgba(90,20,14,.30),transparent 50%); }}
  .center-stamp::before {{ content:""; position:absolute; inset:8px; border:1.5px solid rgba(243,236,221,.5); }}
  .stamp-zi {{ font-size: 60px; color: var(--paper); font-weight: 700; line-height: 1; }}
  .center-item {{ color: var(--muted); font-size: 0.8rem; line-height: 1.9; letter-spacing: .08em; }}
  .palace-header {{ display: flex; align-items: center; gap: 4px; margin-bottom: 5px; padding-bottom: 3px; border-bottom: .5px solid var(--line); flex-wrap: wrap; }}
  .palace-stem-branch {{ color: var(--gold); font-size: 0.72rem; font-weight: 700; margin-left: auto; order: 2; }}
  .palace-name {{ color: var(--vermil-d); font-size: 0.78rem; letter-spacing: .06em; order: 1; }}
  .palace-stars {{ font-size: 0.82rem; line-height: 1.6; color: var(--ink); }}
  .star-major {{ color: var(--ink); font-weight: 700; }}
  .star-minor {{ color: var(--muted); }}
  .star-minor.tough {{ color: var(--vermil); }}
  .star-adj {{ color: #9a8e78; font-size: 0.7em; }}
  .brightness {{ color: var(--muted); font-size: 0.66em; margin-left: 1px; }}
  .decadal {{ color: var(--muted); font-size: 0.66rem; margin-top: 4px; }}
  .badge {{ font-size: 0.62rem; padding: 1px 5px; font-weight: 700; border: 1px solid var(--vermil); color: var(--vermil); border-radius: 2px; order: 3; }}
  .badge.soul {{ background: var(--vermil); color: var(--paper); }}
  .badge.body {{ background: var(--paper); color: var(--vermil); }}

  /* Reading Cards · 解读卡 */
  .reading-section {{ margin-bottom: 32px; }}
  .reading-grid {{ display: flex; flex-wrap: wrap; gap: 16px; }}
  .reading-card {{ background: var(--paper2); border: 1px solid var(--gold); box-shadow: 0 0 0 3px var(--paper),0 0 0 4px var(--vermil); padding: 22px 20px; flex: 1; min-width: 280px; position: relative; }}
  .card-full {{ flex-basis: 100%; }}
  .card-half {{ flex-basis: calc(50% - 8px); }}
  .card-highlight {{ box-shadow: 0 0 0 3px var(--paper),0 0 0 4px var(--gold); border-color: var(--vermil); }}
  .card-teal {{ border-color: var(--vermil); }}
  .card-title {{ color: var(--ink); font-size: 1.1rem; letter-spacing: .06em; margin-bottom: 12px; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
  .card-badge {{ background: var(--vermil); color: var(--paper); font-size: 0.78rem; padding: 3px 12px; letter-spacing: .12em; font-weight: normal; }}
  .card-body {{ color: var(--ink); font-size: 0.92rem; line-height: 1.9; }}
  .card-body strong {{ color: var(--vermil-d); }}
  .card-body em {{ color: var(--gold); font-style: normal; font-weight: 700; }}
  .card-body .warn {{ color: var(--vermil); font-weight: 700; }}
  .card-body .good {{ color: var(--good); font-weight: 700; }}

  /* Probability bars · 置信度 */
  .prob-bars {{ margin-top: 16px; display: flex; flex-direction: column; gap: 8px; }}
  .prob-item {{ display: flex; align-items: center; gap: 10px; }}
  .prob-label {{ color: var(--muted); font-size: 0.75rem; width: 120px; flex-shrink: 0; letter-spacing: .05em; }}
  .prob-bar-bg {{ flex: 1; height: 6px; background: rgba(201,183,155,.4); border: .5px solid var(--line); overflow: hidden; }}
  .prob-bar-fill {{ height: 100%; background: var(--vermil); }}
  .prob-pct {{ color: var(--vermil-d); font-size: 0.75rem; width: 36px; text-align: right; font-weight: 700; }}

  /* Hand reading · 手相 */
  .hand-section {{ margin-bottom: 32px; }}
  .hand-grid {{ display: flex; flex-wrap: wrap; gap: 16px; }}
  .hand-item {{ background: var(--paper2); border: 1px solid var(--line); padding: 16px; flex: 1; min-width: 220px; }}
  .hand-item-title {{ color: var(--vermil-d); font-size: 0.9rem; font-weight: 700; margin-bottom: 6px; letter-spacing: .05em; }}
  .hand-item-body {{ color: var(--ink); font-size: 0.85rem; line-height: 1.75; margin-bottom: 8px; }}
  .hand-status {{ font-size: 0.75rem; padding: 3px 10px; display: inline-block; border: .5px solid; }}
  .status-match {{ color: var(--good); border-color: var(--good); }}
  .status-conflict {{ color: var(--vermil); border-color: var(--vermil); }}
  .resolution {{ color: var(--muted); font-size: 0.8rem; margin-top: 6px; }}

  /* Calibration · 校准 */
  .calibration-section {{ background: var(--paper2); border: 1px solid var(--gold); box-shadow: 0 0 0 3px var(--paper),0 0 0 4px var(--vermil); padding: 24px 22px; margin-bottom: 32px; }}
  .section-title {{ color: var(--vermil); font-size: 1.15rem; margin-bottom: 14px; letter-spacing: .12em; }}
  .cal-note {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 16px; letter-spacing: .04em; }}
  .cal-questions {{ display: flex; flex-direction: column; gap: 10px; }}
  .cal-question {{ background: var(--paper); border: .5px solid var(--line); padding: 14px; }}
  .cal-text {{ color: var(--ink); font-size: 0.9rem; }}
  .cal-hint {{ color: var(--muted); font-size: 0.8rem; margin-top: 4px; }}

  .footer {{ text-align: center; color: var(--muted); font-size: 0.78rem; padding: 26px 0; border-top: 1px solid var(--line); margin-top: 34px; letter-spacing: .12em; }}
  .footer .footer-en {{ font-family: 'Times New Roman',serif; display: block; margin-top: 6px; letter-spacing: .3em; color: var(--gold); }}
  .colophon {{ display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 18px; }}
  .brand-seal {{ width: 34px; height: 34px; background: var(--vermil); color: var(--paper); font-weight: 700; font-size: 20px; display: flex; align-items: center; justify-content: center; border-radius: 3px; transform: rotate(-4deg); position: relative; background-image: radial-gradient(circle at 70% 75%,rgba(90,20,14,.30),transparent 55%); }}
  .brand-seal::before {{ content:""; position:absolute; inset:3px; border:1px solid rgba(243,236,221,.5); border-radius:2px; }}
  .colophon .brand-txt {{ font-size: 0.72rem; color: var(--muted); letter-spacing: .12em; text-align: left; line-height: 1.5; }}
  .colophon .brand-txt b {{ color: var(--vermil-d); font-weight: 700; }}
  @media (max-width: 600px) {{
    .card-half {{ flex-basis: 100%; }}
    .palace-cell {{ padding: 4px; }}
    .palace-name {{ font-size: 0.72rem; }}
    .header-title {{ font-size: 2rem; }}
  }}
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <div class="header-en">Purple Star Astrology · Destiny Chart</div>
    <div class="header-title">紫微命盘</div>
    <div class="header-sub">{chart_data.get("lunar_date","")} · {chart_data.get("gender","")} · {chart_data.get("hour_name","")}</div>
    {f'<div class="decadal-banner">当前大限 · {current_decadal}</div>' if current_decadal else ''}
  </div>

  <div class="grid-section">
    <table class="palace-grid">
      {grid_html}
    </table>
  </div>

  <div class="reading-section">
    <div class="reading-grid">
      {cards_html}
    </div>
  </div>

  {hand_html}
  {cal_html}

  <div class="footer">
    象由心生 · 命由象推　命盘显示可能性，行动决定现实
    <span class="footer-en">A map of probabilities, not a verdict.</span>
    <div class="colophon">
      <span class="brand-seal">真</span>
      <span class="brand-txt"><b>真斗</b> · TrueStars<br>紫微斗数 · 只说真话的命理</span>
    </div>
  </div>
</div>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"HTML 已生成：{output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chart', required=True)
    parser.add_argument('--reading', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    with open(args.chart, encoding='utf-8') as f:
        chart_data = json.load(f)
    with open(args.reading, encoding='utf-8') as f:
        reading_data = json.load(f)

    generate_html(chart_data, reading_data, args.output)


if __name__ == '__main__':
    main()
