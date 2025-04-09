"""
手串饰品预测软件 - DeepSeek API集成模块 (Vercel版本)
提供与DeepSeek API的集成功能
"""
import os
import json
import requests

# DeepSeek API配置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-b21ed31cf5f34cf483602422613aac4c")
DEEPSEEK_API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

def get_enhanced_prediction(user_info, basic_prediction):
    """
    使用DeepSeek API增强预测结果
    
    参数:
        user_info: 用户基本信息
        basic_prediction: 基本预测结果
        
    返回:
        增强的预测结果
    """
    try:
        # 检查网络连接
        if not is_network_available():
            return {
                'enhanced': False,
                'error': '网络连接不可用',
                'message': '无法连接到DeepSeek API，使用基本预测结果'
            }
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        # 构建提示信息
        prompt = create_prompt(basic_prediction)
        
        # 构建请求体
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一位精通命理学、风水学和手串饰品的专家顾问，擅长根据用户的命理特征提供个性化的运势预测和手串饰品推荐。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        # 发送请求
        response = requests.post(DEEPSEEK_API_ENDPOINT, headers=headers, data=json.dumps(data), timeout=30)
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            enhanced_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 解析增强内容
            enhanced_prediction = parse_enhanced_content(enhanced_content)
            enhanced_prediction['enhanced'] = True
            return enhanced_prediction
        else:
            return {
                'enhanced': False,
                'error': f"API请求失败: {response.status_code}",
                'message': '无法获取增强预测，使用基本预测结果'
            }
    
    except Exception as e:
        return {
            'enhanced': False,
            'error': str(e),
            'message': '获取增强预测时出错，使用基本预测结果'
        }

def create_prompt(basic_prediction):
    """
    创建DeepSeek API请求的提示信息
    
    参数:
        basic_prediction: 基本预测结果
        
    返回:
        提示信息
    """
    name = basic_prediction.get('name', '')
    gender = basic_prediction.get('gender', '')
    birth_date = basic_prediction.get('birth_date', '')
    zodiac = basic_prediction.get('zodiac', '')
    zodiac_sign = basic_prediction.get('zodiac_sign', '')
    eight_characters = basic_prediction.get('eight_characters', {})
    five_elements = basic_prediction.get('five_elements', [])
    purpose = basic_prediction.get('purpose', '')
    religion = basic_prediction.get('religion', '')
    
    prompt = f"""
请根据以下用户信息，提供详细和个性化的命运预测和手串饰品推荐：

用户信息:
- 姓名: {name}
- 性别: {gender}
- 出生日期: {birth_date}
- 生肖: {zodiac}
- 星座: {zodiac_sign}
- 八字: {json.dumps(eight_characters, ensure_ascii=False)}
- 五行: {', '.join(five_elements)}
- 所求事项: {purpose}
- 宗教信仰: {religion}

请提供以下内容:
1. 详细的流年运势分析，包括事业、财运、健康、感情等方面
2. 针对用户所求事项({purpose})的深入建议
3. 个性化的手串饰品推荐，包括材质、颜色、配饰等
4. 佩戴手串的注意事项和增强效果的方法

请以JSON格式回复，包含以下字段:
- yearly_fortune: 流年运势分析
- purpose_advice: 所求事项建议
- bracelet_recommendation: 手串推荐
- usage_tips: 使用建议
"""
    
    return prompt

def parse_enhanced_content(content):
    """
    解析DeepSeek API返回的增强内容
    
    参数:
        content: API返回的内容
        
    返回:
        解析后的预测结果
    """
    try:
        # 尝试解析JSON
        if content.strip().startswith('{') and content.strip().endswith('}'):
            enhanced_data = json.loads(content)
        else:
            # 尝试提取JSON部分
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                json_str = content[start_idx:end_idx+1]
                enhanced_data = json.loads(json_str)
            else:
                # 无法解析为JSON，使用文本格式
                enhanced_data = {
                    "yearly_fortune": content,
                    "purpose_advice": "",
                    "bracelet_recommendation": "",
                    "usage_tips": ""
                }
        
        return enhanced_data
    
    except Exception as e:
        return {
            'error': str(e),
            'message': '解析增强内容出错',
            'raw_content': content
        }

def test_deepseek_api():
    """
    测试DeepSeek API连接
    
    返回:
        测试结果
    """
    try:
        # 检查网络连接
        if not is_network_available():
            return {
                'success': False,
                'message': '网络连接不可用'
            }
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        # 构建请求体
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": "你好，这是一个测试消息。请回复'DeepSeek API连接正常'。"}
            ],
            "temperature": 0.7,
            "max_tokens": 50
        }
        
        # 发送请求
        response = requests.post(DEEPSEEK_API_ENDPOINT, headers=headers, data=json.dumps(data), timeout=10)
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {
                'success': True,
                'message': '连接成功',
                'response': content
            }
        else:
            return {
                'success': False,
                'message': f"API请求失败: {response.status_code}",
                'response': response.text
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': f"连接出错: {str(e)}"
        }

def is_network_available():
    """
    检查网络连接是否可用
    
    返回:
        布尔值，表示网络是否可用
    """
    try:
        # 尝试连接到百度
        response = requests.get('https://www.baidu.com', timeout=5)
        return response.status_code == 200
    except:
        return False
