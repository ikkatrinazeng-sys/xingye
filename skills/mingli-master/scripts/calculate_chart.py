#!/usr/bin/env python3
"""紫微斗数排盘脚本，使用 iztro-py 库"""

import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(description='紫微斗数排盘')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--solar', help='公历日期 YYYY-M-D')
    group.add_argument('--lunar', help='农历日期 YYYY-M-D')
    parser.add_argument('--hour', type=int, required=True,
                        help='时辰索引 0=早子 1=丑 2=寅 3=卯 4=辰 5=巳 6=午 7=未 8=申 9=酉 10=戌 11=亥 12=晚子')
    parser.add_argument('--gender', required=True, help='性别 男/女')
    parser.add_argument('--output', required=True, help='输出 JSON 文件路径')
    args = parser.parse_args()

    try:
        sys.path.insert(0, '/Users/cengkexin/Library/Python/3.9/lib/python/site-packages')
        from iztro_py import astro
    except ImportError:
        print("请先安装 iztro-py: python3 -m pip install iztro-py --user", file=sys.stderr)
        sys.exit(1)

    hour_map = {
        0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6,
        7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 23
    }
    birth_hour = hour_map.get(args.hour, args.hour)

    try:
        if args.solar:
            astrolabe = astro.by_solar(args.solar, args.hour, args.gender)
        else:
            astrolabe = astro.by_lunar(args.lunar, args.hour, args.gender)
    except Exception as e:
        print(f"排盘失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 序列化命盘数据
    result = serialize_astrolabe(astrolabe, args.gender, args.hour)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"排盘完成，已写入 {args.output}")


def safe_str(obj):
    """安全转换为字符串"""
    if obj is None:
        return ''
    return str(obj)


def serialize_star(star):
    """序列化星曜"""
    try:
        return {
            'name': safe_str(getattr(star, 'name', '')),
            'type': safe_str(getattr(star, 'type', '')),
            'scope': safe_str(getattr(star, 'scope', '')),
            'brightness': safe_str(getattr(star, 'brightness', '')),
            'mutagen': safe_str(getattr(star, 'mutagen', '')),
        }
    except Exception:
        return {'name': safe_str(star), 'type': '', 'scope': '', 'brightness': '', 'mutagen': ''}


def serialize_palace(palace):
    """序列化宫位"""
    try:
        major_stars = []
        minor_stars = []
        adjunct_stars = []

        for s in (getattr(palace, 'majorStars', None) or []):
            major_stars.append(serialize_star(s))
        for s in (getattr(palace, 'minorStars', None) or []):
            minor_stars.append(serialize_star(s))
        for s in (getattr(palace, 'adjunctStars', None) or []):
            adjunct_stars.append(serialize_star(s))

        decadal = getattr(palace, 'decadal', None)
        decadal_data = None
        if decadal:
            decadal_data = {
                'range': list(getattr(decadal, 'range', []) or []),
                'heavenlyStem': safe_str(getattr(decadal, 'heavenlyStem', '')),
                'earthlyBranch': safe_str(getattr(decadal, 'earthlyBranch', '')),
            }

        ages = getattr(palace, 'ages', None) or []

        return {
            'name': safe_str(getattr(palace, 'name', '')),
            'heavenlyStem': safe_str(getattr(palace, 'heavenlyStem', '')),
            'earthlyBranch': safe_str(getattr(palace, 'earthlyBranch', '')),
            'isBodyPalace': bool(getattr(palace, 'isBodyPalace', False)),
            'isOriginalPalace': bool(getattr(palace, 'isOriginalPalace', False)),
            'majorStars': major_stars,
            'minorStars': minor_stars,
            'adjunctStars': adjunct_stars,
            'decadal': decadal_data,
            'ages': list(ages),
        }
    except Exception as e:
        return {'name': '?', 'error': str(e), 'majorStars': [], 'minorStars': [], 'adjunctStars': []}


def serialize_astrolabe(astrolabe, gender, hour_index):
    """序列化整个命盘"""
    hour_names = ['早子时', '丑时', '寅时', '卯时', '辰时', '巳时', '午时',
                  '未时', '申时', '酉时', '戌时', '亥时', '晚子时']
    hour_name = hour_names[hour_index] if 0 <= hour_index <= 12 else f'时辰{hour_index}'

    palaces = []
    for p in (getattr(astrolabe, 'palaces', None) or []):
        palaces.append(serialize_palace(p))

    fiveElementsClass = safe_str(getattr(astrolabe, 'fiveElementsClass', ''))

    return {
        'gender': gender,
        'hour_index': hour_index,
        'hour_name': hour_name,
        'solarDate': safe_str(getattr(astrolabe, 'solarDate', '')),
        'lunarDate': safe_str(getattr(astrolabe, 'lunarDate', '')),
        'chineseDate': safe_str(getattr(astrolabe, 'chineseDate', '')),
        'rawDates': {
            'heavenlyStemAndEarthlyBranch': safe_str(getattr(astrolabe, 'rawDates', {}) and getattr(getattr(astrolabe, 'rawDates', None), 'heavenlyStemAndEarthlyBranch', '') if hasattr(getattr(astrolabe, 'rawDates', None), 'heavenlyStemAndEarthlyBranch') else ''),
        },
        'fiveElementsClass': fiveElementsClass,
        'palaces': palaces,
    }


if __name__ == '__main__':
    main()
