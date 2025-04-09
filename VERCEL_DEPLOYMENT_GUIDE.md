"""
手串饰品预测软件 - Vercel部署指南
"""

# Vercel部署指南

## 简介

本文档提供了将手串饰品预测系统部署到Vercel的详细步骤。Vercel是一个云平台，专为前端开发者和设计师打造，可以轻松部署网站和Web应用程序。

## 准备工作

1. **创建Vercel账号**
   - 访问 https://vercel.com/signup
   - 您可以使用GitHub、GitLab、Bitbucket账号登录，或使用邮箱注册
   - 建议使用GitHub账号，这样部署会更简单

2. **准备应用代码**
   - 确保您已经下载了手串饰品预测系统的所有文件
   - 确保文件结构正确，包含所有必要的文件

## 部署步骤

### 方法一：直接从GitHub部署（推荐）

1. **创建GitHub仓库**
   - 登录您的GitHub账号
   - 点击右上角"+"图标，选择"New repository"
   - 仓库名称填写"feng-shui-bracelet-app"
   - 选择"Public"（公开）
   - 点击"Create repository"

2. **上传代码到GitHub**
   - 您可以使用GitHub Desktop或直接在网页上上传文件
   - 将以下文件上传到仓库：
     - vercel.json
     - requirements.txt
     - app_vercel.py（重命名为app.py）
     - lunar_solar_converter_vercel.py（重命名为lunar_solar_converter.py）
     - deepseek_api_vercel.py（重命名为deepseek_api.py）
     - storage_vercel.py（重命名为storage.py）
     - templates/（整个目录）
     - static/（整个目录）

3. **在Vercel上部署**
   - 登录Vercel账号
   - 点击"Add New..."，然后选择"Project"
   - 选择您刚才创建的GitHub仓库
   - Vercel会自动检测项目类型，确认是Python项目
   - 在"Environment Variables"部分，添加DeepSeek API密钥：
     - NAME: DEEPSEEK_API_KEY
     - VALUE: sk-b21ed31cf5f34cf483602422613aac4c
   - 点击"Deploy"按钮开始部署

4. **等待部署完成**
   - Vercel会自动构建和部署您的应用
   - 部署完成后，您会看到一个成功的提示和应用的URL
   - 这个URL就是您的手串饰品预测系统的在线地址

### 方法二：使用Vercel CLI（命令行工具）

如果您熟悉命令行操作，也可以使用Vercel CLI进行部署：

1. **安装Vercel CLI**
   ```
   npm install -g vercel
   ```

2. **登录Vercel**
   ```
   vercel login
   ```

3. **部署项目**
   - 进入项目目录
   ```
   cd path/to/feng_shui_bracelet_app_server
   ```
   - 确保文件名正确（app.py而不是app_vercel.py等）
   - 执行部署命令
   ```
   vercel --prod
   ```

## 部署后的操作

1. **访问您的应用**
   - 使用Vercel提供的URL访问您的手串饰品预测系统
   - 例如：https://feng-shui-bracelet-app.vercel.app

2. **分享应用**
   - 您可以将这个URL分享给任何人，他们都可以通过浏览器访问您的应用
   - 无需安装任何软件，直接在浏览器中使用所有功能

3. **更新应用**
   - 如果您需要更新应用，只需更新GitHub仓库中的代码
   - Vercel会自动检测更新并重新部署

## 常见问题解答

1. **应用部署后无法访问**
   - 检查部署日志，查看是否有错误信息
   - 确保所有必要的文件都已上传
   - 确保环境变量已正确设置

2. **DeepSeek API不工作**
   - 检查环境变量是否正确设置
   - 确保API密钥有效
   - 检查网络连接是否正常

3. **数据存储问题**
   - Vercel的函数计算环境是无状态的，数据存储在/tmp目录中是临时的
   - 如果需要永久存储数据，建议使用数据库服务

## 联系支持

如果您在部署过程中遇到任何问题，请联系我们的支持团队获取帮助。

---

祝您使用愉快！
