import os
import requests
import json
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from knowledge_base import KB

# 加载环境变量
load_dotenv()

app = Flask(__name__, static_folder='frontend/dist', static_url_path='')
CORS(app)  # 启用CORS

# Google Gemini API密钥和URL
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_API_KEY}"

# 配置代理（如果.env中定义了代理设置）
proxies = {}
if os.getenv("HTTP_PROXY"):
    proxies["http"] = os.getenv("HTTP_PROXY")
if os.getenv("HTTPS_PROXY"):
    proxies["https"] = os.getenv("HTTPS_PROXY")

# 离线回答库 - 在API不可用时使用
offline_responses = [
    "根据我的理解，这个问题涉及到...",
    "这个问题有几个方面需要考虑...",
    "从历史数据来看，这种情况通常...",
    "在分析这个问题时，我们需要考虑多个因素...",
    "这是一个有趣的问题，让我来尝试解释...",
    "在我的数据库中，关于这个主题的信息显示...",
    "正在模拟AI思考过程...[离线模式]"
]

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/ask', methods=['POST'])
def ask():
    user_question = request.json.get('question', '')
    use_knowledge_base = request.json.get('use_knowledge_base', True)
    
    if not user_question:
        return jsonify({"error": "问题不能为空"}), 400
    
    try:
        # 从知识库获取相关上下文（如果启用知识库）
        context = ""
        if use_knowledge_base:
            context = KB.get_context_for_question(user_question)
            
        # 准备API请求
        headers = {
            'Content-Type': 'application/json'
        }
        
        # 根据是否有知识库上下文构建不同的提示
        if context:
            prompt = f"""以下是与问题相关的知识库内容:
            
{context}

基于上述知识库内容，请回答问题: {user_question}

如果知识库内容不足以回答问题，请使用您自己的知识，但优先考虑知识库内容。
"""
        else:
            prompt = user_question
            
        payload = {
            "contents": [{
                "parts":[{"text": prompt}]
            }]
        }
        
        try:
            # 发送请求到Gemini API，使用可配置的代理和SSL验证设置
            response = requests.post(
                GEMINI_API_URL,
                headers=headers,
                data=json.dumps(payload),
                verify=False,  # 禁用SSL验证
                proxies=proxies if proxies else None,
                timeout=30  # 设置30秒超时
            )
            
            # 检查响应
            response.raise_for_status()
            result = response.json()
            
            # 从响应中提取文本
            answer = ""
            if "candidates" in result and len(result["candidates"]) > 0:
                for part in result["candidates"][0]["content"]["parts"]:
                    if "text" in part:
                        answer += part["text"]
            
            if not answer:
                answer = "抱歉，我无法生成回答。"
                
            # # 如果使用了知识库，添加注释
            # if context and use_knowledge_base:
            #     answer += "\n\n[回答基于知识库提供的信息]"
        
        except (requests.exceptions.RequestException, KeyError, ValueError) as api_error:
            # API调用失败，使用离线回答
            print(f"API调用失败，使用离线回答: {str(api_error)}")
            answer = f"{random.choice(offline_responses)}\n\n[离线回答 - API连接失败: {type(api_error).__name__}]"
            
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": f"请求处理失败: {str(e)}"}), 500

@app.route('/api/upload_document', methods=['POST'])
def upload_document():
    """上传文档到知识库"""
    if 'file' not in request.files:
        return jsonify({"error": "没有文件"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "没有选择文件"}), 400
        
    # 检查文件类型
    if not (file.filename.endswith('.pdf') or file.filename.endswith('.txt')):
        return jsonify({"error": "只支持PDF和TXT文件"}), 400
        
    # 保存文件到临时位置
    temp_path = os.path.join('temp', file.filename)
    os.makedirs('temp', exist_ok=True)
    file.save(temp_path)
    
    # 添加到知识库
    success, message = KB.add_document(temp_path)
    
    # 删除临时文件
    try:
        os.remove(temp_path)
    except:
        pass
        
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400

@app.route('/api/knowledge_base_status', methods=['GET'])
def knowledge_base_status():
    """获取知识库状态"""
    has_index = KB.vector_store is not None
    
    # 获取知识库文档列表
    documents = []
    if os.path.exists(KB.documents_dir):
        for filename in os.listdir(KB.documents_dir):
            file_path = os.path.join(KB.documents_dir, filename)
            if os.path.isfile(file_path) and not (filename == "faiss_index" or filename == "documents.pkl"):
                documents.append(filename)
    
    return jsonify({
        "active": has_index,
        "document_count": len(documents),
        "documents": documents
    })

# 创建知识库索引路由
@app.route('/api/create_index', methods=['POST'])
def create_index():
    """创建或重新创建知识库索引"""
    success = KB.create_index()
    if success:
        return jsonify({"message": "知识库索引创建成功"}), 200
    else:
        return jsonify({"error": "知识库索引创建失败，可能是没有文档"}), 400

# 抑制不安全连接警告（仅用于开发）
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if __name__ == '__main__':
    # 确保临时目录存在
    os.makedirs('temp', exist_ok=True)
    # 尝试加载知识库索引
    app.run(debug=True, host='0.0.0.0', port=5000) 