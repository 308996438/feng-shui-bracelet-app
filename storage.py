"""
手串饰品预测软件 - 数据存储模块 (Vercel版本)
提供预测结果和分享链接的存储功能
"""
import os
import json
import time
import uuid
import datetime

# 存储目录
STORAGE_DIR = "/tmp/feng_shui_bracelet_storage"

# 确保存储目录存在
def ensure_storage_dir():
    """确保存储目录存在"""
    os.makedirs(STORAGE_DIR, exist_ok=True)
    os.makedirs(os.path.join(STORAGE_DIR, "predictions"), exist_ok=True)
    os.makedirs(os.path.join(STORAGE_DIR, "shares"), exist_ok=True)

# 保存预测结果
def save_prediction(prediction):
    """
    保存预测结果
    
    参数:
        prediction: 预测结果
        
    返回:
        预测结果ID
    """
    ensure_storage_dir()
    
    # 生成唯一ID
    prediction_id = str(uuid.uuid4())
    
    # 添加时间戳
    prediction['timestamp'] = time.time()
    
    # 保存预测结果
    prediction_file = os.path.join(STORAGE_DIR, "predictions", f"{prediction_id}.json")
    with open(prediction_file, 'w', encoding='utf-8') as f:
        json.dump(prediction, f, ensure_ascii=False, indent=2)
    
    return prediction_id

# 获取预测结果
def get_prediction(prediction_id):
    """
    获取预测结果
    
    参数:
        prediction_id: 预测结果ID
        
    返回:
        预测结果，如果不存在则返回None
    """
    ensure_storage_dir()
    
    # 检查预测结果是否存在
    prediction_file = os.path.join(STORAGE_DIR, "predictions", f"{prediction_id}.json")
    if not os.path.exists(prediction_file):
        return None
    
    # 读取预测结果
    try:
        with open(prediction_file, 'r', encoding='utf-8') as f:
            prediction = json.load(f)
        return prediction
    except Exception:
        return None

# 保存分享链接
def save_share(prediction_id, expire_days=7):
    """
    保存分享链接
    
    参数:
        prediction_id: 预测结果ID
        expire_days: 过期天数
        
    返回:
        分享ID
    """
    ensure_storage_dir()
    
    # 生成唯一ID
    share_id = str(uuid.uuid4())
    
    # 计算过期时间
    expire_time = time.time() + expire_days * 24 * 60 * 60
    
    # 保存分享信息
    share_info = {
        'prediction_id': prediction_id,
        'expire_time': expire_time,
        'created_time': time.time()
    }
    
    share_file = os.path.join(STORAGE_DIR, "shares", f"{share_id}.json")
    with open(share_file, 'w', encoding='utf-8') as f:
        json.dump(share_info, f, ensure_ascii=False, indent=2)
    
    return share_id

# 获取分享的预测结果
def get_prediction_by_share(share_id):
    """
    获取分享的预测结果
    
    参数:
        share_id: 分享ID
        
    返回:
        预测结果，如果不存在或已过期则返回None
    """
    ensure_storage_dir()
    
    # 检查分享是否存在
    share_file = os.path.join(STORAGE_DIR, "shares", f"{share_id}.json")
    if not os.path.exists(share_file):
        return None
    
    # 读取分享信息
    try:
        with open(share_file, 'r', encoding='utf-8') as f:
            share_info = json.load(f)
        
        # 检查是否过期
        if time.time() > share_info.get('expire_time', 0):
            return None
        
        # 获取预测结果
        prediction_id = share_info.get('prediction_id')
        if not prediction_id:
            return None
        
        return get_prediction(prediction_id)
    except Exception:
        return None

# 清理过期的分享
def cleanup_expired_shares():
    """清理过期的分享"""
    ensure_storage_dir()
    
    # 获取所有分享文件
    shares_dir = os.path.join(STORAGE_DIR, "shares")
    share_files = os.listdir(shares_dir)
    
    # 当前时间
    current_time = time.time()
    
    # 检查每个分享是否过期
    for share_file in share_files:
        if not share_file.endswith('.json'):
            continue
        
        share_path = os.path.join(shares_dir, share_file)
        try:
            with open(share_path, 'r', encoding='utf-8') as f:
                share_info = json.load(f)
            
            # 如果过期，删除文件
            if current_time > share_info.get('expire_time', 0):
                os.remove(share_path)
        except Exception:
            # 如果读取出错，也删除文件
            try:
                os.remove(share_path)
            except Exception:
                pass
