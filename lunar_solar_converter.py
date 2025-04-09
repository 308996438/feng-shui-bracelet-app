"""
手串饰品预测软件 - 阴阳历转换模块
提供阴历阳历互转、八字计算、星座判断等功能
"""
from lunarcalendar import Converter, Solar, Lunar, DateNotExist
import datetime

def solar_to_lunar(year, month, day):
    """
    阳历转阴历
    
    参数:
        year: 阳历年份
        month: 阳历月份
        day: 阳历日期
        
    返回:
        包含阴历日期信息的字典
    """
    try:
        # 创建阳历日期对象
        solar_date = Solar(year, month, day)
        
        # 转换为阴历
        lunar_date = Converter.Solar2Lunar(solar_date)
        
        # 获取生肖
        zodiac_animals = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
        zodiac = zodiac_animals[(year - 4) % 12]
        
        # 返回结果
        return {
            'lunar_year': lunar_date.year,
            'lunar_month': lunar_date.month,
            'lunar_day': lunar_date.day,
            'is_leap_month': lunar_date.isLeapMonth,
            'lunar_date': f"{lunar_date.year}年{'闰' if lunar_date.isLeapMonth else ''}{lunar_date.month}月{lunar_date.day}日",
            'zodiac': zodiac,
            'solar_date': datetime.date(year, month, day)
        }
    except DateNotExist:
        raise ValueError("无效的阳历日期")
    except Exception as e:
        raise ValueError(f"阳历转阴历出错: {str(e)}")

def lunar_to_solar(year, month, day, is_leap_month=False):
    """
    阴历转阳历
    
    参数:
        year: 阴历年份
        month: 阴历月份
        day: 阴历日期
        is_leap_month: 是否闰月
        
    返回:
        包含阳历日期信息的字典
    """
    try:
        # 创建阴历日期对象
        lunar_date = Lunar(year, month, day, is_leap_month)
        
        # 转换为阳历
        solar_date = Converter.Lunar2Solar(lunar_date)
        
        # 获取生肖
        zodiac_animals = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
        zodiac = zodiac_animals[(year - 4) % 12]
        
        # 返回结果
        return {
            'solar_year': solar_date.year,
            'solar_month': solar_date.month,
            'solar_day': solar_date.day,
            'solar_date': datetime.date(solar_date.year, solar_date.month, solar_date.day),
            'lunar_date': f"{year}年{'闰' if is_leap_month else ''}{month}月{day}日",
            'zodiac': zodiac
        }
    except DateNotExist:
        raise ValueError("无效的阴历日期")
    except Exception as e:
        raise ValueError(f"阴历转阳历出错: {str(e)}")

def get_zodiac_sign(month, day):
    """
    获取星座
    
    参数:
        month: 阳历月份
        day: 阳历日期
        
    返回:
        星座名称
    """
    dates = [20, 19, 21, 20, 21, 22, 23, 23, 23, 24, 22, 21]
    signs = ['摩羯座', '水瓶座', '双鱼座', '白羊座', '金牛座', '双子座', 
             '巨蟹座', '狮子座', '处女座', '天秤座', '天蝎座', '射手座', '摩羯座']
    
    if day < dates[month-1]:
        return signs[month-1]
    else:
        return signs[month]

def get_hour_ganzhi(year, month, day, hour):
    """
    获取时辰干支
    
    参数:
        year: 阳历年份
        month: 阳历月份
        day: 阳历日期
        hour: 小时(0-23)
        
    返回:
        时辰干支
    """
    # 天干
    heavenly_stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    # 地支
    earthly_branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    # 时辰对应的地支
    hour_to_earthly_branch = [
        0, 0, 0, 0, 0,  # 0-4点为子时
        1, 1,           # 5-6点为丑时
        2, 2,           # 7-8点为寅时
        3, 3,           # 9-10点为卯时
        4, 4,           # 11-12点为辰时
        5, 5,           # 13-14点为巳时
        6, 6,           # 15-16点为午时
        7, 7,           # 17-18点为未时
        8, 8,           # 19-20点为申时
        9, 9,           # 21-22点为酉时
        10, 10,         # 23-24点为戌时
        11, 11          # 25-26点为亥时(实际上是第二天的1-2点)
    ]
    
    # 获取日干支
    solar_date = datetime.date(year, month, day)
    base_date = datetime.date(1900, 1, 1)  # 1900年1月1日为甲子日
    days_diff = (solar_date - base_date).days
    day_stem_index = (days_diff + 10) % 10  # 日天干索引
    
    # 计算时辰天干
    hour_branch_index = hour_to_earthly_branch[hour % 24]
    hour_stem_index = (day_stem_index * 2 + hour_branch_index) % 10
    
    # 返回时辰干支
    return heavenly_stems[hour_stem_index] + earthly_branches[hour_branch_index]

def get_eight_characters(year, month, day, hour=12, is_lunar=False):
    """
    获取八字(四柱)
    
    参数:
        year: 年份
        month: 月份
        day: 日期
        hour: 小时(0-23)
        is_lunar: 是否为阴历日期
        
    返回:
        包含八字信息的字典
    """
    try:
        # 如果是阴历日期，转换为阳历
        if is_lunar:
            solar_info = lunar_to_solar(year, month, day)
            solar_date = solar_info['solar_date']
        else:
            solar_date = datetime.date(year, month, day)
        
        # 天干
        heavenly_stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        # 地支
        earthly_branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 计算年柱
        # 以立春为界，立春前算上一年
        # 简化处理，使用固定日期：2月4日
        if solar_date.month == 1 or (solar_date.month == 2 and solar_date.day < 4):
            year_offset = -1
        else:
            year_offset = 0
        
        year_stem_index = (solar_date.year + year_offset - 4) % 10
        year_branch_index = (solar_date.year + year_offset - 4) % 12
        
        # 计算月柱
        # 以节气为界，每个月的节气日期大约是：
        # 1月：6日小寒，21日大寒
        # 2月：4日立春，19日雨水
        # 3月：6日惊蛰，21日春分
        # 4月：5日清明，20日谷雨
        # 5月：6日立夏，21日小满
        # 6月：6日芒种，21日夏至
        # 7月：7日小暑，23日大暑
        # 8月：8日立秋，23日处暑
        # 9月：8日白露，23日秋分
        # 10月：8日寒露，24日霜降
        # 11月：7日立冬，22日小雪
        # 12月：7日大雪，22日冬至
        
        # 简化处理，使用固定日期
        month_boundaries = [0, 6, 4, 6, 5, 6, 6, 7, 8, 8, 8, 7, 7]
        
        if solar_date.day < month_boundaries[solar_date.month]:
            month_offset = -1
        else:
            month_offset = 0
        
        # 计算月干支
        # 甲己年的正月起丙寅
        # 乙庚年的正月起戊寅
        # 丙辛年的正月起庚寅
        # 丁壬年的正月起壬寅
        # 戊癸年的正月起甲寅
        month_index = (solar_date.month + month_offset - 1) % 12
        if month_index <= 0:
            month_index += 12
        
        year_stem = year_stem_index % 5
        month_stem_index = (year_stem * 2 + month_index + 1) % 10
        month_branch_index = (month_index + 1) % 12
        
        # 计算日柱
        base_date = datetime.date(1900, 1, 1)  # 1900年1月1日为甲子日
        days_diff = (solar_date - base_date).days
        day_stem_index = (days_diff + 10) % 10
        day_branch_index = (days_diff + 12) % 12
        
        # 计算时柱
        hour_ganzhi = get_hour_ganzhi(solar_date.year, solar_date.month, solar_date.day, hour)
        
        # 返回八字
        return {
            'year': heavenly_stems[year_stem_index] + earthly_branches[year_branch_index],
            'month': heavenly_stems[month_stem_index] + earthly_branches[month_branch_index],
            'day': heavenly_stems[day_stem_index] + earthly_branches[day_branch_index],
            'hour': hour_ganzhi
        }
    except Exception as e:
        raise ValueError(f"计算八字出错: {str(e)}")

def is_valid_solar_date(year, month, day):
    """
    检查阳历日期是否有效
    
    参数:
        year: 年份
        month: 月份
        day: 日期
        
    返回:
        布尔值，表示日期是否有效
    """
    try:
        datetime.date(year, month, day)
        return True
    except ValueError:
        return False

def is_valid_lunar_date(year, month, day, is_leap_month=False):
    """
    检查阴历日期是否有效
    
    参数:
        year: 年份
        month: 月份
        day: 日期
        is_leap_month: 是否闰月
        
    返回:
        布尔值，表示日期是否有效
    """
    try:
        lunar_date = Lunar(year, month, day, is_leap_month)
        Converter.Lunar2Solar(lunar_date)
        return True
    except DateNotExist:
        return False
    except Exception:
        return False
