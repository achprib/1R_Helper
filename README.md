# 1R Helper

这是一个基于Vue.js + Flask的AI问答助手，使用Google Gemini API提供回答功能。
在.env中设置API及代理

## 功能特点

- 基于Vue.js的前端界面
- Flask后端API服务
- 实时问答交互
- 基于Google Gemini API的AI回答

## 项目结构

```
/
├── ai_assistant.py        # Flask后端服务
├── .env                   # 环境变量配置
├── requirements.txt       # Python依赖
└── frontend/              # Vue.js前端
    ├── src/               # Vue源代码
    ├── public/            # 静态资源
    ├── dist/              # 构建输出目录
    ├── package.json       # NPM配置
    └── ...
```

## 安装步骤

### 后端设置

1. 安装Python依赖：
```bash
pip install -r requirements.txt
```

2. 配置API密钥：
   - 在项目根目录找到`.env`文件
   - 将`your_api_key_here`替换为您的Google Gemini API密钥

### 前端设置

1. 安装Node.js依赖：
```bash
cd frontend
npm install
```

2. 构建前端代码：
```bash
npm run build
```

## 使用方法

### 开发模式

1. 启动后端服务：
```bash
python ai_assistant.py
```

2. 另一个终端中启动前端开发服务器：
```bash
cd frontend
npm run serve
```

3. 访问开发服务器：
```
http://localhost:8080
```

### 生产模式

1. 构建前端：
```bash
cd frontend
npm run build
```

2. 启动Flask服务：
```bash
python ai_assistant.py
```

3. 访问应用：
```
http://localhost:5000
```

## 系统要求

- Python 3.7+
- Node.js 14+
- 网络连接（用于访问Google Gemini API）

## 注意事项

- 使用前请确保您已获取有效的Google Gemini API密钥
- 您可以在 https://ai.google.dev/ 注册并获取API密钥 