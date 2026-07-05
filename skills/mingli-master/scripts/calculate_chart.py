#!/usr/bin/env python3
"""紫微斗数排盘脚本，使用 iztro-py 库

真太阳时校正：
  中国全境用东八区（120°E）北京时间，各地实际经度不同，钟表时间≠当地太阳时。
  经度时差 = (出生地经度 − 120) × 4 分钟。出生在时辰交界附近时，这个偏移
  可能把命宫推到隔壁宫，整张盘就变了。故务必用精确出生时间 + 经度做校正。
"""

import argparse
import json
import sys
import datetime
import math

# 常见城市经度（东经，度）。找不到时用 --longitude 直接传。
CITY_LONGITUDE = {
    '北京': 116.4, '上海': 121.5, '天津': 117.2, '重庆': 106.5,
    '广州': 113.3, '深圳': 114.1, '珠海': 113.6, '东莞': 113.8,
    '杭州': 120.2, '南京': 118.8, '苏州': 120.6, '无锡': 120.3,
    '扬州': 119.4, '济南': 117.0, '青岛': 120.4, '郑州': 113.6,
    '武汉': 114.3, '长沙': 112.9, '郴州': 112.9, '衡阳': 112.6,
    '株洲': 113.1, '岳阳': 113.1, '南昌': 115.9, '合肥': 117.3,
    '福州': 119.3, '厦门': 118.1, '成都': 104.1, '昆明': 102.7,
    '贵阳': 106.6, '西安': 108.9, '兰州': 103.8, '西宁': 101.8,
    '银川': 106.3, '太原': 112.5, '石家庄': 114.5, '沈阳': 123.4,
    '大连': 121.6, '长春': 125.3, '哈尔滨': 126.6, '呼和浩特': 111.7,
    '南宁': 108.4, '海口': 110.3, '拉萨': 91.1, '乌鲁木齐': 87.6,
}

STANDARD_MERIDIAN = 120.0  # 东八区标准经线


def city_longitude(name):
    """按城市名查经度，支持'郴州市''郴州'等写法。查不到返回 None。"""
    if not name:
        return None
    key = name.replace('市', '').replace('省', '').strip()
    for city, lon in CITY_LONGITUDE.items():
        if city in key or key in city:
            return lon
    return None


def equation_of_time(dt):
    """均时差（分钟），真太阳时与平太阳时之差的近似值，范围约 ±16 分钟。"""
    n = dt.timetuple().tm_yday
    b = 2 * math.pi * (n - 81) / 364.0
    return 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)


def time_to_hour_index(hh, mm):
    """由钟点(时,分)推时辰索引。0=早子(00-01) 1=丑 ... 11=亥 12=晚子(23-24)。"""
    total = hh * 60 + mm
    if total >= 23 * 60:
        return 12          # 晚子时 23:00-24:00
    if total < 60:
        return 0           # 早子时 00:00-01:00
    # 丑时起，每两小时一格，从 01:00 开始
    return (total - 60) // 120 + 1


def apply_true_solar_time(solar_date, hh, mm, longitude, use_eot=False):
    """对钟表时间做真太阳时校正，返回校正后的 (日期字符串, 时辰索引, 校正详情)。"""
    delta_lon = (longitude - STANDARD_MERIDIAN) * 4.0   # 经度时差(分钟)
    dt = datetime.datetime.strptime(solar_date, '%Y-%m-%d').replace(hour=hh, minute=mm)
    delta_eot = equation_of_time(dt) if use_eot else 0.0
    corrected = dt + datetime.timedelta(minutes=delta_lon + delta_eot)

    naive_idx = time_to_hour_index(hh, mm)
    corr_idx = time_to_hour_index(corrected.hour, corrected.minute)
    detail = {
        'birthplace_longitude': round(longitude, 2),
        'longitude_delta_min': round(delta_lon, 1),
        'equation_of_time_min': round(delta_eot, 1) if use_eot else None,
        'clock_time': f'{hh:02d}:{mm:02d}',
        'true_solar_time': corrected.strftime('%Y-%m-%d %H:%M'),
        'naive_hour_index': naive_idx,
        'corrected_hour_index': corr_idx,
        'crossed_boundary': naive_idx != corr_idx,
    }
    return corrected.strftime('%Y-%m-%d'), corr_idx, detail


def main():
    parser = argparse.ArgumentParser(description='紫微斗数排盘')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--solar', help='公历日期 YYYY-M-D')
    group.add_argument('--lunar', help='农历日期 YYYY-M-D')
    parser.add_argument('--hour', type=int,
                        help='时辰索引 0=早子 1=丑 2=寅 3=卯 4=辰 5=巳 6=午 7=未 8=申 9=酉 10=戌 11=亥 12=晚子（只知道时辰、无精确时间时用）')
    parser.add_argument('--time', help='精确出生时间 HH:MM（配合 --longitude/--city 做真太阳时校正，优先于 --hour）')
    parser.add_argument('--longitude', type=float, help='出生地经度（东经，度），用于真太阳时校正')
    parser.add_argument('--city', help='出生城市名（自动查经度，如"郴州"）；与 --longitude 二选一')
    parser.add_argument('--eot', action='store_true', help='同时计入均时差（equation of time），更精确')
    parser.add_argument('--gender', required=True, help='性别 男/女')
    parser.add_argument('--output', required=True, help='输出 JSON 文件路径')
    args = parser.parse_args()

    try:
        sys.path.insert(0, '/Users/cengkexin/Library/Python/3.9/lib/python/site-packages')
        from iztro_py import astro
    except ImportError:
        print("请先安装 iztro-py: python3 -m pip install iztro-py --user", file=sys.stderr)
        sys.exit(1)

    # ---- 真太阳时校正 ----
    correction = None
    hour_index = args.hour
    solar_date = args.solar

    if args.time:
        # 有精确时间：尝试做经度校正
        try:
            hh, mm = (int(x) for x in args.time.split(':'))
        except ValueError:
            print("--time 格式应为 HH:MM，如 10:00", file=sys.stderr)
            sys.exit(1)

        longitude = args.longitude
        if longitude is None and args.city:
            longitude = city_longitude(args.city)
            if longitude is None:
                print(f"未收录城市「{args.city}」的经度，请改用 --longitude 直接传经度", file=sys.stderr)
                sys.exit(1)

        if longitude is not None and args.solar:
            solar_date, hour_index, correction = apply_true_solar_time(
                args.solar, hh, mm, longitude, use_eot=args.eot)
            if correction['crossed_boundary']:
                names = ['早子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥','晚子']
                print(f"⚠ 真太阳时校正：钟表 {correction['clock_time']} → 真太阳时 "
                      f"{correction['true_solar_time'][-5:]}，跨越时辰边界，"
                      f"由 {names[correction['naive_hour_index']]}时 校正为 "
                      f"{names[correction['corrected_hour_index']]}时。命宫已按校正后时辰排定。",
                      file=sys.stderr)
        else:
            # 有时间但没给经度：退化为直接按时间取时辰，不做校正
            hour_index = time_to_hour_index(hh, mm)
            print("提示：未提供出生地经度，未做真太阳时校正。卡时辰边界者建议补经度。", file=sys.stderr)

    if hour_index is None:
        print("请提供 --hour（时辰索引）或 --time（精确时间）之一", file=sys.stderr)
        sys.exit(1)

    try:
        if args.solar:
            astrolabe = astro.by_solar(solar_date, hour_index, args.gender)
        else:
            astrolabe = astro.by_lunar(args.lunar, hour_index, args.gender)
    except Exception as e:
        print(f"排盘失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 序列化命盘数据
    result = serialize_astrolabe(astrolabe, args.gender, hour_index)
    if correction:
        result['true_solar_time_correction'] = correction

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
