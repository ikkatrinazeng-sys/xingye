#!/usr/bin/env python3
"""八宅命卦排方位（风水，非紫微斗数）。

系统声明：这是风水八宅派，算个人吉凶方位，与紫微斗数是两套系统。
紫微算时间，不算空间方位。用它给"买房方位"参考时必须对用户说明边界。
"""

import argparse
import json
import sys

# 命卦号 → 卦名 / 命组
GUA_NAME = {1: '坎', 2: '坤', 3: '震', 4: '巽', 6: '乾', 7: '兑', 8: '艮', 9: '离'}
EAST_GROUP = {1, 3, 4, 9}   # 东四命
WEST_GROUP = {2, 6, 7, 8}   # 西四命

# 八方中文
DIR_CN = {'N': '正北', 'NE': '东北', 'E': '正东', 'SE': '东南',
          'S': '正南', 'SW': '西南', 'W': '正西', 'NW': '西北'}

# 游年八方表：每个命卦 → {四吉:方位, 四凶:方位}
# 四吉：生气(最旺·财运活力) 天医(健康贵人) 延年(感情婚姻) 伏位(平稳积蓄)
# 四凶：绝命 五鬼 六煞 祸害
YOUNIAN = {
    1: {'生气': 'SE', '天医': 'E',  '延年': 'S',  '伏位': 'N',
        '绝命': 'SW', '五鬼': 'NE', '六煞': 'NW', '祸害': 'W'},
    9: {'生气': 'E',  '天医': 'SE', '延年': 'N',  '伏位': 'S',
        '绝命': 'NW', '五鬼': 'W',  '六煞': 'NE', '祸害': 'SW'},
    3: {'生气': 'S',  '天医': 'N',  '延年': 'SE', '伏位': 'E',
        '绝命': 'W',  '五鬼': 'NW', '六煞': 'SW', '祸害': 'NE'},
    4: {'生气': 'N',  '天医': 'S',  '延年': 'E',  '伏位': 'SE',
        '绝命': 'NE', '五鬼': 'SW', '六煞': 'W',  '祸害': 'NW'},
    6: {'生气': 'W',  '天医': 'NE', '延年': 'SW', '伏位': 'NW',
        '绝命': 'S',  '五鬼': 'E',  '六煞': 'N',  '祸害': 'SE'},
    2: {'生气': 'NE', '天医': 'W',  '延年': 'NW', '伏位': 'SW',
        '绝命': 'N',  '五鬼': 'SE', '六煞': 'S',  '祸害': 'E'},
    8: {'生气': 'SW', '天医': 'NW', '延年': 'W',  '伏位': 'NE',
        '绝命': 'SE', '五鬼': 'N',  '六煞': 'E',  '祸害': 'S'},
    7: {'生气': 'NW', '天医': 'SW', '延年': 'NE', '伏位': 'W',
        '绝命': 'E',  '五鬼': 'S',  '六煞': 'SE', '祸害': 'N'},
}

JI_MEANING = {'生气': '最旺 · 事业财运、活力',
              '天医': '健康、贵人、稳定',
              '延年': '感情、婚姻、人际和谐',
              '伏位': '平稳、积蓄'}


def digit_root(n):
    """反复相加到个位。"""
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n


def life_gua(year, gender):
    """由出生年+性别求命卦号。gender: 男/女。"""
    root = digit_root(sum(int(c) for c in str(year)[-2:]))
    male = gender.startswith('男')
    if year < 2000:
        g = (10 - root) if male else (root + 5)
    else:  # 2000 及以后
        g = (9 - root) if male else (root + 6)
    g = digit_root(g)
    # 中宫寄卦：男归2坤，女归8艮
    if g == 5:
        g = 2 if male else 8
    return g


def analyze(year, gender):
    g = life_gua(year, gender)
    group = '东四命' if g in EAST_GROUP else '西四命'
    yn = YOUNIAN[g]
    ji = {k: yn[k] for k in ('生气', '天医', '延年', '伏位')}
    xiong = {k: yn[k] for k in ('绝命', '五鬼', '六煞', '祸害')}
    return {
        'year': year, 'gender': gender,
        'gua_number': g, 'gua_name': GUA_NAME[g], 'group': group,
        'auspicious': {k: {'dir': v, 'dir_cn': DIR_CN[v], 'meaning': JI_MEANING[k]}
                       for k, v in ji.items()},
        'inauspicious': {k: {'dir': v, 'dir_cn': DIR_CN[v]} for k, v in xiong.items()},
    }


def main():
    p = argparse.ArgumentParser(description='八宅命卦方位（风水）')
    p.add_argument('--year', type=int, required=True, help='出生公历年份，如 1995')
    p.add_argument('--gender', required=True, help='性别 男/女')
    p.add_argument('--output', help='可选：输出 JSON 路径')
    args = p.parse_args()

    r = analyze(args.year, args.gender)
    print(f"命卦：{r['gua_name']}卦（{r['group']}）")
    print("四吉方：")
    for k, v in r['auspicious'].items():
        print(f"  {k}　{v['dir_cn']}　—— {v['meaning']}")
    print("四凶方（避）：", '、'.join(v['dir_cn'] for v in r['inauspicious'].values()))
    print("\n⚠ 这是风水八宅方位，非紫微斗数。落地到具体房子仍需看坐向、门向、周边形势。")

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(r, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
