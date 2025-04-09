"""
手串饰品预测软件服务器端应用 - Vercel版本
提供阴阳历转换、命理预测和手串推荐功能的API
"""
from flask import Flask, request, jsonify, render_template, redirect, url_for
import datetime
import json
import os
import requests
from lunar_solar_converter import (
    solar_to_lunar, lunar_to_solar, get_eight_characters,
    get_zodiac_sign, get_hour_ganzhi, is_valid_lunar_date, is_valid_solar_date
)
from deepseek_api import get_enhanced_prediction, test_deepseek_api
from storage import save_prediction, get_prediction, save_share, get_prediction_by_share, cleanup_expired_shares

app = Flask(__name__)

# DeepSeek API密钥 - 从环境变量获取或使用默认值
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-b21ed31cf5f34cf483602422613aac4c")
DEEPSEEK_API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

# 五行属性
FIVE_ELEMENTS = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
    "子": "水", "亥": "水",
    "寅": "木", "卯": "木",
    "巳": "火", "午": "火",
    "申": "金", "酉": "金",
    "丑": "土", "辰": "土", "未": "土", "戌": "土"
}

# 手串材质数据
BRACELET_MATERIALS = {
    "水晶": {
        "五行": "水",
        "颜色": ["透明", "白色", "紫色", "粉色", "黄色", "绿色", "蓝色"],
        "功效": ["净化能量", "增强直觉", "提升精神力"],
        "适合人群": ["需要净化负能量的人", "追求心灵平静的人"]
    },
    "琉璃": {
        "五行": "火",
        "颜色": ["蓝色", "绿色", "红色", "黄色", "紫色"],
        "功效": ["辟邪", "招财", "增强运势"],
        "适合人群": ["追求美好事物的人", "需要提升运势的人"]
    },
    "和田玉": {
        "五行": "土",
        "颜色": ["白色", "青白色", "青色", "黄色"],
        "功效": ["养生", "平衡情绪", "增强体质"],
        "适合人群": ["注重健康的人", "需要情绪稳定的人"]
    },
    "翡翠": {
        "五行": "木",
        "颜色": ["绿色", "紫色", "红色", "白色"],
        "功效": ["招财", "辟邪", "保平安"],
        "适合人群": ["追求财富的人", "需要保平安的人"]
    },
    "星月菩提": {
        "五行": "木",
        "颜色": ["棕色", "红棕色"],
        "功效": ["静心", "开智慧", "增强记忆力"],
        "适合人群": ["修行者", "学生", "需要静心的人"]
    },
    "金刚菩提": {
        "五行": "木",
        "颜色": ["棕色", "红棕色"],
        "功效": ["辟邪", "增强意志力", "提升自信"],
        "适合人群": ["需要增强意志力的人", "需要提升自信的人"]
    },
    "小叶紫檀": {
        "五行": "木",
        "颜色": ["紫红色", "深棕色"],
        "功效": ["安神", "辟邪", "增强气场"],
        "适合人群": ["睡眠质量差的人", "需要提升气场的人"]
    },
    "沉香": {
        "五行": "木",
        "颜色": ["棕色", "黄棕色"],
        "功效": ["静心", "提升灵性", "改善呼吸系统"],
        "适合人群": ["修行者", "呼吸系统不佳的人"]
    },
    "檀香": {
        "五行": "木",
        "颜色": ["黄色", "棕黄色"],
        "功效": ["安神", "净化空间", "提升专注力"],
        "适合人群": ["需要提升专注力的人", "睡眠质量差的人"]
    },
    "蜜蜡": {
        "五行": "土",
        "颜色": ["黄色", "棕黄色", "红黄色"],
        "功效": ["招财", "保平安", "增强健康"],
        "适合人群": ["追求财富的人", "注重健康的人"]
    },
    "砗磲": {
        "五行": "水",
        "颜色": ["白色", "米白色"],
        "功效": ["增强智慧", "提升运势", "改善人际关系"],
        "适合人群": ["需要提升智慧的人", "人际关系不佳的人"]
    },
    "玛瑙": {
        "五行": "火",
        "颜色": ["红色", "橙色", "蓝色", "绿色", "紫色"],
        "功效": ["增强勇气", "提升自信", "保平安"],
        "适合人群": ["需要增强勇气的人", "需要提升自信的人"]
    },
    "青金石": {
        "五行": "水",
        "颜色": ["蓝色", "深蓝色"],
        "功效": ["增强直觉", "提升智慧", "改善沟通能力"],
        "适合人群": ["需要提升智慧的人", "沟通能力不佳的人"]
    },
    "珊瑚": {
        "五行": "火",
        "颜色": ["红色", "粉红色", "白色"],
        "功效": ["招财", "辟邪", "增强血液循环"],
        "适合人群": ["追求财富的人", "血液循环不佳的人"]
    },
    "松石": {
        "五行": "水",
        "颜色": ["蓝绿色", "绿色"],
        "功效": ["保平安", "增强运势", "改善呼吸系统"],
        "适合人群": ["需要保平安的人", "呼吸系统不佳的人"]
    },
    "南红玛瑙": {
        "五行": "火",
        "颜色": ["红色", "橙红色"],
        "功效": ["招财", "增强运势", "提升活力"],
        "适合人群": ["追求财富的人", "需要提升活力的人"]
    },
    "黄龙玉": {
        "五行": "土",
        "颜色": ["黄色", "绿色", "白色"],
        "功效": ["招财", "增强健康", "提升运势"],
        "适合人群": ["追求财富的人", "注重健康的人"]
    },
    "佛珠": {
        "五行": "木",
        "颜色": ["棕色", "黑色", "红色"],
        "功效": ["静心", "开智慧", "增强灵性"],
        "适合人群": ["修行者", "需要静心的人"]
    }
}

# 宗教信仰对应的吉祥物和符号
RELIGIOUS_SYMBOLS = {
    '佛教': ['佛珠', '莲花', '法轮', '卍字符', '佛像', '六字真言'],
    '道教': ['太极', '八卦', '五行', '道符', '如意', '灵芝'],
    '基督教': ['十字架', '鱼形符号', '圣经', '天使', '橄榄枝', '鸽子'],
    '无': ['如意', '福字', '寿字', '平安结', '铜钱', '龙凤']
}

# 宗教特色手串材质
RELIGIOUS_MATERIALS = {
    '佛教': ['菩提子', '檀香木', '金刚菩提', '凤眼菩提', '星月菩提', '砗磲', '绿松石'],
    '道教': ['黄杨木', '桃木', '檀木', '紫檀', '黑檀', '玉石', '水晶'],
    '基督教': ['橄榄木', '黑檀木', '紫檀木', '水晶', '玛瑙', '橄榄石'],
    '无': ['黄花梨', '小叶紫檀', '沉香', '金丝楠', '鸡翅木', '红木', '乌木']
}

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/result')
def result():
    """预测结果页面"""
    return render_template('result.html')

@app.route('/share')
def share():
    """分享预测结果页面"""
    return render_template('share.html')

@app.route('/api/convert/solar-to-lunar', methods=['POST'])
def api_solar_to_lunar():
    """阳历转阴历API"""
    data = request.get_json()
    
    try:
        year = int(data.get('year'))
        month = int(data.get('month'))
        day = int(data.get('day'))
        
        # 验证日期
        if not is_valid_solar_date(year, month, day):
            return jsonify({'error': '无效的阳历日期'}), 400
        
        # 转换日期
        result = solar_to_lunar(year, month, day)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/convert/lunar-to-solar', methods=['POST'])
def api_lunar_to_solar():
    """阴历转阳历API"""
    data = request.get_json()
    
    try:
        year = int(data.get('year'))
        month = int(data.get('month'))
        day = int(data.get('day'))
        is_leap_month = bool(data.get('is_leap_month', False))
        
        # 验证日期
        if not is_valid_lunar_date(year, month, day, is_leap_month):
            return jsonify({'error': '无效的阴历日期'}), 400
        
        # 转换日期
        result = lunar_to_solar(year, month, day, is_leap_month)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/calculate/eight-characters', methods=['POST'])
def api_calculate_eight_characters():
    """计算八字API"""
    data = request.get_json()
    
    try:
        year = int(data.get('year'))
        month = int(data.get('month'))
        day = int(data.get('day'))
        hour = int(data.get('hour', 12))
        is_lunar = bool(data.get('is_lunar', False))
        
        # 计算八字
        result = get_eight_characters(year, month, day, hour, is_lunar)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/predict/fortune', methods=['POST'])
def api_predict_fortune():
    """命运预测API"""
    data = request.get_json()
    
    try:
        # 获取基本信息
        name = data.get('name', '')
        gender = data.get('gender', '')
        birth_year = int(data.get('birth_year'))
        birth_month = int(data.get('birth_month'))
        birth_day = int(data.get('birth_day'))
        birth_hour = int(data.get('birth_hour', 12))
        is_lunar_date = bool(data.get('is_lunar_date', False))
        purpose = data.get('purpose', '财运')
        religion = data.get('religion', '无')
        birth_place = data.get('birth_place', '')
        
        # 如果是阴历日期，转换为阳历
        if is_lunar_date:
            solar_info = lunar_to_solar(birth_year, birth_month, birth_day)
            birth_date = solar_info['solar_date']
        else:
            birth_date = datetime.date(birth_year, birth_month, birth_day)
        
        # 获取八字
        eight_characters = get_eight_characters(birth_year, birth_month, birth_day, birth_hour, is_lunar_date)
        
        # 获取星座
        zodiac_sign = get_zodiac_sign(birth_date.month, birth_date.day)
        
        # 获取生肖
        lunar_info = solar_to_lunar(birth_date.year, birth_date.month, birth_date.day)
        zodiac = lunar_info['zodiac']
        
        # 获取五行属性
        five_elements = []
        for pillar in eight_characters.values():
            for char in pillar:
                if char in FIVE_ELEMENTS:
                    element = FIVE_ELEMENTS[char]
                    if element not in five_elements:
                        five_elements.append(element)
        
        # 计算幸运数字
        lucky_number1 = (birth_date.day + birth_date.month) % 9 + 1
        lucky_number2 = (birth_date.year % 100) % 9 + 1
        if lucky_number1 == lucky_number2:
            lucky_number2 = (lucky_number2 % 9) + 1
        lucky_numbers = [lucky_number1, lucky_number2]
        
        # 获取幸运颜色
        color_map = {
            "木": ["绿色", "青色"],
            "火": ["红色", "紫色"],
            "土": ["黄色", "棕色"],
            "金": ["白色", "金色"],
            "水": ["黑色", "蓝色"]
        }
        
        lucky_colors = []
        for element in five_elements:
            if element in color_map:
                lucky_colors.extend(color_map[element])
        
        # 生成基本预测结果
        basic_prediction = {
            'name': name,
            'gender': gender,
            'birth_date': str(birth_date),
            'birth_time': f"{birth_hour}:00",
            'birth_place': birth_place,
            'zodiac': zodiac,
            'zodiac_sign': zodiac_sign,
            'eight_characters': eight_characters,
            'five_elements': five_elements,
            'lucky_numbers': lucky_numbers,
            'lucky_colors': lucky_colors,
            'purpose': purpose,
            'religion': religion
        }
        
        # 使用DeepSeek API增强预测
        user_info = {
            'name': name,
            'gender': gender,
            'birth_date': str(birth_date),
            'birth_time': f"{birth_hour}:00",
            'birth_place': birth_place,
            'purpose': purpose,
            'religion': religion
        }
        enhanced_prediction = get_enhanced_prediction(user_info, basic_prediction)
        
        # 推荐手串
        bracelet_recommendation = recommend_bracelet(basic_prediction, enhanced_prediction)
        
        # 合并结果
        result = {
            'basic_prediction': basic_prediction,
            'enhanced_prediction': enhanced_prediction,
            'bracelet_recommendation': bracelet_recommendation
        }
        
        # 保存预测结果
        prediction_id = save_prediction(result)
        result['id'] = prediction_id
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/share', methods=['POST'])
def api_create_share():
    """创建分享链接API"""
    data = request.get_json()
    
    try:
        prediction_id = data.get('prediction_id')
        if not prediction_id:
            return jsonify({'error': '缺少预测结果ID'}), 400
        
        # 创建分享
        share_id = save_share(prediction_id)
        
        # 生成分享链接
        share_url = request.host_url.rstrip('/') + url_for('share') + f'?id={share_id}'
        
        return jsonify({
            'share_id': share_id,
            'share_url': share_url
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/share/<share_id>', methods=['GET'])
def api_get_shared_prediction(share_id):
    """获取分享的预测结果API"""
    try:
        # 获取预测结果
        prediction = get_prediction_by_share(share_id)
        
        if not prediction:
            return jsonify({'error': '无效的分享ID或分享已过期'}), 404
        
        return jsonify(prediction)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/test/deepseek', methods=['GET'])
def api_test_deepseek():
    """测试DeepSeek API连接"""
    try:
        result = test_deepseek_api()
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def is_network_available():
    """检查网络连接是否可用"""
    try:
        # 尝试连接到百度
        response = requests.get('https://www.baidu.com', timeout=5)
        return response.status_code == 200
    except:
        return False

def recommend_bracelet(basic_prediction, enhanced_prediction):
    """推荐手串"""
    try:
        # 获取基本信息
        five_elements = basic_prediction.get('five_elements', [])
        lucky_colors = basic_prediction.get('lucky_colors', [])
        purpose = basic_prediction.get('purpose', '财运')
        religion = basic_prediction.get('religion', '无')
        
        # 获取增强预测中的手串推荐
        enhanced_bracelet = enhanced_prediction.get('bracelet_recommendation', '')
        
        # 如果有增强预测的手串推荐，直接使用
        if enhanced_bracelet and enhanced_prediction.get('enhanced', False):
            return {
                'source': 'enhanced',
                'recommendation': enhanced_bracelet
            }
        
        # 否则，使用基本算法推荐
        # 根据五行属性选择材质
        missing_elements = []
        all_elements = ['木', '火', '土', '金', '水']
        for element in all_elements:
            if element not in five_elements:
                missing_elements.append(element)
        
        # 如果没有缺失的五行，选择与所求事项相关的五行
        if not missing_elements:
            if purpose == '财运':
                missing_elements = ['金', '木']
            elif purpose == '事业':
                missing_elements = ['火', '木']
            elif purpose == '健康':
                missing_elements = ['土', '金']
            elif purpose == '婚姻':
                missing_elements = ['火', '土']
            elif purpose == '学业':
                missing_elements = ['水', '木']
            elif purpose == '人际':
                missing_elements = ['火', '木']
            elif purpose == '破小人':
                missing_elements = ['金', '水']
            else:
                missing_elements = ['土']
        
        # 选择材质
        recommended_materials = []
        for material, info in BRACELET_MATERIALS.items():
            if info['五行'] in missing_elements:
                # 检查是否有幸运颜色
                has_lucky_color = False
                for color in info['颜色']:
                    if color in lucky_colors:
                        has_lucky_color = True
                        break
                
                recommended_materials.append({
                    'name': material,
                    'element': info['五行'],
                    'colors': info['颜色'],
                    'effects': info['功效'],
                    'suitable_for': info['适合人群'],
                    'has_lucky_color': has_lucky_color
                })
        
        # 根据宗教信仰选择特色材质
        religious_materials = RELIGIOUS_MATERIALS.get(religion, [])
        for material in religious_materials:
            if material in BRACELET_MATERIALS:
                info = BRACELET_MATERIALS[material]
                # 检查是否已经推荐过
                already_recommended = False
                for rec in recommended_materials:
                    if rec['name'] == material:
                        already_recommended = True
                        break
                
                if not already_recommended:
                    # 检查是否有幸运颜色
                    has_lucky_color = False
                    for color in info['颜色']:
                        if color in lucky_colors:
                            has_lucky_color = True
                            break
                    
                    recommended_materials.append({
                        'name': material,
                        'element': info['五行'],
                        'colors': info['颜色'],
                        'effects': info['功效'],
                        'suitable_for': info['适合人群'],
                        'has_lucky_color': has_lucky_color,
                        'religious': True
                    })
        
        # 选择宗教符号
        religious_symbols = RELIGIOUS_SYMBOLS.get(religion, [])
        
        # 生成推荐文本
        recommendation_text = f"根据您的五行属性和{purpose}需求，推荐以下手串材质组合：\n\n"
        
        # 添加材质描述
        for i, material in enumerate(recommended_materials[:3]):
            recommendation_text += f"{i+1}. {material['name']}（{material['element']}属性）\n"
            recommendation_text += f"   颜色：{', '.join(material['colors'])}\n"
            recommendation_text += f"   功效：{', '.join(material['effects'])}\n"
            recommendation_text += f"   适合：{', '.join(material['suitable_for'])}\n\n"
        
        # 添加宗教符号建议
        if religious_symbols:
            recommendation_text += f"根据您的{religion}信仰，建议在手串上添加以下吉祥物或符号：\n"
            recommendation_text += f"{', '.join(religious_symbols[:3])}\n\n"
        
        # 添加佩戴建议
        recommendation_text += "佩戴建议：\n"
        recommendation_text += "1. 手串通常佩戴在左手，因为左手靠近心脏，能更好地吸收能量。\n"
        recommendation_text += "2. 新购买的手串最好先净化，可以用清水冲洗或放在阳光下晒一晒。\n"
        recommendation_text += "3. 佩戴时保持心态平和，有助于增强手串的效果。\n"
        recommendation_text += "4. 定期清洁手串，保持其能量纯净。\n"
        
        return {
            'source': 'basic',
            'missing_elements': missing_elements,
            'materials': recommended_materials[:3],
            'religious_symbols': religious_symbols[:3],
            'recommendation': recommendation_text
        }
    
    except Exception as e:
        return {
            'source': 'error',
            'error': str(e),
            'recommendation': f"手串推荐生成出错：{str(e)}"
        }

# Vercel入口点
app = app

# 如果直接运行此脚本，则启动Flask应用
if __name__ == '__main__':
    # 清理过期的分享
    cleanup_expired_shares()
    # 从环境变量获取端口，如果没有则使用8080
    port = int(os.environ.get('PORT', 8080))
    # 启动应用
    app.run(host='0.0.0.0', port=port)
