/**
 * 手串饰品预测系统主要JavaScript文件
 * 处理表单提交、API请求和页面交互
 */

// 当文档加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化日期选择器
    initDateSelectors();
    
    // 初始化表单提交处理
    initFormSubmission();
    
    // 初始化分享功能
    initShareFeatures();
    
    // 初始化PDF导出功能
    initPdfExport();
});

/**
 * 初始化日期选择器
 */
function initDateSelectors() {
    // 获取年月日选择器元素
    const yearSelect = document.getElementById('birthYear');
    const monthSelect = document.getElementById('birthMonth');
    const daySelect = document.getElementById('birthDay');
    const dateTypeRadios = document.getElementsByName('dateType');
    
    // 如果页面上没有这些元素，直接返回
    if (!yearSelect || !monthSelect || !daySelect) return;
    
    // 生成年份选项（1940-当前年份）
    const currentYear = new Date().getFullYear();
    for (let year = currentYear; year >= 1940; year--) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year + '年';
        yearSelect.appendChild(option);
    }
    
    // 生成月份选项
    for (let month = 1; month <= 12; month++) {
        const option = document.createElement('option');
        option.value = month;
        option.textContent = month + '月';
        monthSelect.appendChild(option);
    }
    
    // 更新日期选项的函数
    function updateDays() {
        const year = parseInt(yearSelect.value) || currentYear;
        const month = parseInt(monthSelect.value) || 1;
        const isLunar = document.getElementById('lunarDate').checked;
        
        // 清空现有选项
        daySelect.innerHTML = '<option value="">请选择</option>';
        
        // 如果是阳历，直接计算当月天数
        if (!isLunar) {
            const daysInMonth = new Date(year, month, 0).getDate();
            for (let day = 1; day <= daysInMonth; day++) {
                const option = document.createElement('option');
                option.value = day;
                option.textContent = day + '日';
                daySelect.appendChild(option);
            }
        } else {
            // 如果是阴历，默认每月30天（简化处理）
            // 实际应用中应该调用API获取准确的阴历月份天数
            const daysInLunarMonth = 30;
            for (let day = 1; day <= daysInLunarMonth; day++) {
                const option = document.createElement('option');
                option.value = day;
                option.textContent = day + '日';
                daySelect.appendChild(option);
            }
        }
    }
    
    // 监听年月变化，更新日期选项
    yearSelect.addEventListener('change', updateDays);
    monthSelect.addEventListener('change', updateDays);
    
    // 监听日期类型变化
    for (const radio of dateTypeRadios) {
        radio.addEventListener('change', updateDays);
    }
    
    // 初始化日期选项
    updateDays();
}

/**
 * 初始化表单提交处理
 */
function initFormSubmission() {
    const predictionForm = document.getElementById('predictionForm');
    if (!predictionForm) return;
    
    predictionForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 显示加载提示
        showLoading('正在生成预测结果，请稍候...');
        
        // 获取表单数据
        const formData = new FormData(this);
        const jsonData = {};
        
        // 转换为JSON对象
        for (const [key, value] of formData.entries()) {
            jsonData[key] = value;
        }
        
        // 添加阴历/阳历标记
        jsonData.is_lunar_date = document.getElementById('lunarDate').checked;
        
        // 发送API请求
        fetch('/api/predict/fortune', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jsonData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('网络响应不正常');
            }
            return response.json();
        })
        .then(data => {
            // 隐藏加载提示
            hideLoading();
            
            // 保存结果到本地存储
            localStorage.setItem('prediction_result', JSON.stringify(data));
            
            // 跳转到结果页面
            window.location.href = '/result';
        })
        .catch(error => {
            // 隐藏加载提示
            hideLoading();
            
            console.error('提交表单出错:', error);
            showError('提交失败，请稍后重试');
        });
    });
}

/**
 * 初始化分享功能
 */
function initShareFeatures() {
    const shareButton = document.getElementById('shareButton');
    if (!shareButton) return;
    
    shareButton.addEventListener('click', function() {
        // 获取预测结果ID
        const resultData = JSON.parse(localStorage.getItem('prediction_result'));
        if (!resultData || !resultData.id) {
            showError('无法分享，预测结果不完整');
            return;
        }
        
        // 显示加载提示
        showLoading('正在生成分享链接，请稍候...');
        
        // 发送API请求创建分享
        fetch('/api/share', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prediction_id: resultData.id
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('网络响应不正常');
            }
            return response.json();
        })
        .then(data => {
            // 隐藏加载提示
            hideLoading();
            
            // 显示分享链接
            showShareLink(data.share_url);
            
            // 生成二维码
            generateQRCode(data.share_url);
        })
        .catch(error => {
            // 隐藏加载提示
            hideLoading();
            
            console.error('创建分享出错:', error);
            showError('创建分享失败，请稍后重试');
        });
    });
}

/**
 * 初始化PDF导出功能
 */
function initPdfExport() {
    const downloadPdfButton = document.getElementById('downloadPdf');
    if (!downloadPdfButton) return;
    
    downloadPdfButton.addEventListener('click', function() {
        const element = document.getElementById('resultContent');
        const opt = {
            margin: 10,
            filename: '手串饰品预测结果.pdf',
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };
        
        // 显示加载提示
        showLoading('正在生成PDF，请稍候...');
        
        // 生成PDF
        html2pdf().set(opt).from(element).save().then(() => {
            // 隐藏加载提示
            hideLoading();
        });
    });
}

/**
 * 显示加载提示
 */
function showLoading(message) {
    // 检查是否已存在加载提示
    let loadingElement = document.getElementById('loadingOverlay');
    
    if (!loadingElement) {
        // 创建加载提示元素
        loadingElement = document.createElement('div');
        loadingElement.id = 'loadingOverlay';
        loadingElement.style.position = 'fixed';
        loadingElement.style.top = '0';
        loadingElement.style.left = '0';
        loadingElement.style.width = '100%';
        loadingElement.style.height = '100%';
        loadingElement.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        loadingElement.style.display = 'flex';
        loadingElement.style.justifyContent = 'center';
        loadingElement.style.alignItems = 'center';
        loadingElement.style.zIndex = '9999';
        
        const loadingContent = document.createElement('div');
        loadingContent.style.backgroundColor = 'white';
        loadingContent.style.padding = '20px';
        loadingContent.style.borderRadius = '10px';
        loadingContent.style.textAlign = 'center';
        
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        
        const messageElement = document.createElement('p');
        messageElement.id = 'loadingMessage';
        messageElement.style.marginTop = '10px';
        
        loadingContent.appendChild(spinner);
        loadingContent.appendChild(messageElement);
        loadingElement.appendChild(loadingContent);
        document.body.appendChild(loadingElement);
    }
    
    // 更新消息
    document.getElementById('loadingMessage').textContent = message;
    
    // 显示加载提示
    loadingElement.style.display = 'flex';
}

/**
 * 隐藏加载提示
 */
function hideLoading() {
    const loadingElement = document.getElementById('loadingOverlay');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
}

/**
 * 显示错误提示
 */
function showError(message) {
    alert(message);
}

/**
 * 显示分享链接
 */
function showShareLink(url) {
    // 创建模态框
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '9999';
    
    const modalContent = document.createElement('div');
    modalContent.style.backgroundColor = 'white';
    modalContent.style.padding = '20px';
    modalContent.style.borderRadius = '10px';
    modalContent.style.maxWidth = '500px';
    modalContent.style.width = '90%';
    
    const title = document.createElement('h4');
    title.textContent = '分享链接';
    title.style.marginBottom = '15px';
    
    const urlInput = document.createElement('input');
    urlInput.type = 'text';
    urlInput.value = url;
    urlInput.readOnly = true;
    urlInput.style.width = '100%';
    urlInput.style.padding = '8px';
    urlInput.style.marginBottom = '15px';
    urlInput.style.border = '1px solid #ddd';
    urlInput.style.borderRadius = '4px';
    
    const copyButton = document.createElement('button');
    copyButton.textContent = '复制链接';
    copyButton.style.backgroundColor = '#6c5ce7';
    copyButton.style.color = 'white';
    copyButton.style.border = 'none';
    copyButton.style.padding = '8px 15px';
    copyButton.style.borderRadius = '4px';
    copyButton.style.cursor = 'pointer';
    copyButton.style.marginRight = '10px';
    
    const closeButton = document.createElement('button');
    closeButton.textContent = '关闭';
    closeButton.style.backgroundColor = '#6c757d';
    closeButton.style.color = 'white';
    closeButton.style.border = 'none';
    closeButton.style.padding = '8px 15px';
    closeButton.style.borderRadius = '4px';
    closeButton.style.cursor = 'pointer';
    
    // 复制链接功能
    copyButton.addEventListener('click', function() {
        urlInput.select();
        document.execCommand('copy');
        copyButton.textContent = '已复制';
        setTimeout(() => {
            copyButton.textContent = '复制链接';
        }, 2000);
    });
    
    // 关闭模态框
    closeButton.addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    const buttonContainer = document.createElement('div');
    buttonContainer.style.textAlign = 'right';
    buttonContainer.appendChild(copyButton);
    buttonContainer.appendChild(closeButton);
    
    modalContent.appendChild(title);
    modalContent.appendChild(urlInput);
    modalContent.appendChild(buttonContainer);
    modal.appendChild(modalContent);
    
    document.body.appendChild(modal);
}

/**
 * 生成二维码
 */
function generateQRCode(url) {
    const qrcodeContainer = document.getElementById('qrcode');
    if (!qrcodeContainer) return;
    
    // 清空容器
    qrcodeContainer.innerHTML = '';
    
    // 生成二维码
    new QRCode(qrcodeContainer, {
        text: url,
        width: 128,
        height: 128,
        colorDark: '#6c5ce7',
        colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.H
    });
}

/**
 * 格式化八字
 */
function formatEightCharacters(eightChars) {
    if (!eightChars) return '未知';
    return `${eightChars.year} ${eightChars.month} ${eightChars.day} ${eightChars.hour}`;
}

/**
 * 获取时辰名称
 */
function getTimeName(hourGanzhi) {
    if (!hourGanzhi) return '未知';
    const branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
    const timeNames = [
        '子时 (23:00-00:59)', '丑时 (01:00-02:59)', '寅时 (03:00-04:59)', 
        '卯时 (05:00-06:59)', '辰时 (07:00-08:59)', '巳时 (09:00-10:59)',
        '午时 (11:00-12:59)', '未时 (13:00-14:59)', '申时 (15:00-16:59)',
        '酉时 (17:00-18:59)', '戌时 (19:00-20:59)', '亥时 (21:00-22:59)'
    ];
    
    const branch = hourGanzhi[1];
    const index = branches.indexOf(branch);
    return index !== -1 ? timeNames[index] : hourGanzhi;
}

/**
 * 格式化内容，将换行符转换为HTML
 */
function formatContent(content) {
    if (!content) return '<p>暂无数据</p>';
    
    // 替换换行符为<br>
    let formatted = content.replace(/\n/g, '<br>');
    
    // 将列表项格式化
    formatted = formatted.replace(/• (.*?)(<br>|$)/g, '<li>$1</li>');
    formatted = formatted.replace(/\d+\. (.*?)(<br>|$)/g, '<li>$1</li>');
    
    // 如果有列表项，添加ul标签
    if (formatted.includes('<li>')) {
        formatted = formatted.replace(/((?:<li>.*?<\/li>)+)/g, '<ul>$1</ul>');
    }
    
    // 将段落包装在p标签中
    formatted = formatted.replace(/(?:<br>)?(.*?)(?:<br>|<ul>|$)/g, function(match, p1) {
        if (p1.trim() && !p1.includes('<li>') && !p1.includes('</ul>')) {
            return `<p>${p1}</p>`;
        }
        return match;
    });
    
    return formatted;
}
