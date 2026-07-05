#!/usr/bin/env python3
"""流年四化飞宫：算某年的四化星飞入本命哪一宫。

紫微斗数本行——算时间。用于：
  · 买房择年：看三吉化 / 化忌是否飞入【田宅宫】
  · 婚姻择年：看化星是否飞入【夫妻宫】
  · 合盘参考：两人各自流年四化落宫比对
读取 calculate_chart.py 生成的本命 chart.json。
"""

import argparse
import json
import sys

STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 天干四化表：干 → (化禄, 化权, 化科, 化忌)
SIHUA = {
    '甲': ('廉贞', '破军', '武曲', '太阳'),
    '乙': ('天机', '天梁', '紫微', '太阴'),
    '丙': ('天同', '天机', '文昌', '廉贞'),
    '丁': ('太阴', '天同', '天机', '巨门'),
    '戊': ('贪狼', '太阴', '右弼', '天机'),
    '己': ('武曲', '贪狼', '天梁', '文曲'),
    '庚': ('太阳', '武曲', '太阴', '天同'),
    '辛': ('巨门', '太阳', '文曲', '文昌'),
    '壬': ('天梁', '紫微', '左辅', '武曲'),
    '癸': ('破军', '巨门', '太阴', '贪狼'),
}

HUA_LABEL = ['化禄', '化权', '化科', '化忌']


def year_stem(year):
    """公历年 → 年干。甲子年干支循环。"""
    return STEMS[(year - 4) % 10]


def star_palace_map(chart):
    """本命：星名 → 所在宫名。"""
    m = {}
    for p in chart.get('palaces', []):
        for key in ('majorStars', 'minorStars', 'adjunctStars'):
            for s in (p.get(key) or []):
                name = s.get('name', '')
                if name:
                    m[name] = p.get('name', '')
    return m


def year_analysis(year, smap):
    stem = year_stem(year)
    out = []
    for i, star in enumerate(SIHUA[stem]):
        out.append({
            'hua': HUA_LABEL[i],
            'star': star,
            'palace': smap.get(star, '（不在本命盘/辅星未列）'),
        })
    return {'year': year, 'stem': stem, 'transforms': out}


def verdict_for_property(transforms):
    """针对田宅宫给买房吉凶判断。"""
    for t in transforms:
        if t['palace'] == '田宅宫':
            return {
                '化禄': ('吉·置产最强信号', '★首选'),
                '化权': ('吉·主动置产、稳稳拿下', '○有利'),
                '化科': ('吉·改善/文书顺', '○有利'),
                '化忌': ('凶·房产易破财纠纷', '✗避开'),
            }.get(t['hua'], ('', ''))[0] + f"（{t['hua']}{t['star']}入田宅）"
    return '田宅宫无四化飞入，平稳'


def main():
    p = argparse.ArgumentParser(description='流年四化飞宫')
    p.add_argument('--chart', required=True, help='本命 chart.json（calculate_chart.py 产出）')
    p.add_argument('--years', required=True, help='年份范围，如 2026-2032 或单年 2027')
    p.add_argument('--focus', default='all', choices=['all', 'property', 'marriage'],
                   help='关注点：all全部 / property买房(田宅宫) / marriage婚姻(夫妻宫)')
    p.add_argument('--output', help='可选：输出 JSON 路径')
    args = p.parse_args()

    with open(args.chart, encoding='utf-8') as f:
        chart = json.load(f)
    smap = star_palace_map(chart)

    if '-' in args.years:
        a, b = args.years.split('-')
        years = range(int(a), int(b) + 1)
    else:
        years = [int(args.years)]

    results = []
    for y in years:
        ya = year_analysis(y, smap)
        if args.focus == 'property':
            ya['property_verdict'] = verdict_for_property(ya['transforms'])
        results.append(ya)

    # 打印
    for ya in results:
        line = f"{ya['year']}（{ya['stem']}年）: " + '  '.join(
            f"{t['hua']}{t['star']}→{t['palace']}" for t in ya['transforms'])
        print(line)
        if args.focus == 'property':
            print(f"    ▸ 买房判断：{ya['property_verdict']}")

    if args.focus == 'property':
        print("\n提示：买房看【田宅宫】三吉化为吉、化忌避开。合盘买房两人田宅宫都要算，"
              "找一人得吉化、另一人不犯忌的干净年份。")
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
