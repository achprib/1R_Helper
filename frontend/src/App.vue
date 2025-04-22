<template>
  <div class="app-container">
    <div class="header">
      <h1>1R Helper</h1>
    </div>
    
    <div class="chat-container">
      <div class="knowledge-base-panel" v-if="showKbPanel">
        <div class="kb-header">
          <h3>知识库管理</h3>
          <button class="close-btn" @click="showKbPanel = false">×</button>
        </div>
        <div class="kb-content">
          <div class="kb-status">
            <p>
              <span class="status-indicator" :class="{ 'active': kbStatus.active }"></span>
              知识库状态: {{ kbStatus.active ? '已激活' : '未激活' }}
            </p>
            <p>文档数量: {{ kbStatus.document_count }}</p>
          </div>
          
          <div class="kb-documents" v-if="kbStatus.documents.length > 0">
            <h4>已上传文档:</h4>
            <ul>
              <li v-for="(doc, index) in kbStatus.documents" :key="index">
                {{ doc }}
              </li>
            </ul>
          </div>
          
          <div class="kb-upload">
            <h4>上传文档 (支持PDF、TXT):</h4>
            <input type="file" ref="fileInput" @change="handleFileSelected" accept=".pdf,.txt" />
            <button @click="uploadDocument" :disabled="!selectedFile || uploading">
              {{ uploading ? '上传中...' : '上传文档' }}
            </button>
          </div>
          
          <div class="kb-actions">
            <button @click="rebuildIndex" :disabled="indexing">
              {{ indexing ? '索引构建中...' : '重建索引' }}
            </button>
          </div>
        </div>
      </div>
      
      <div class="chat-messages" ref="chatMessages">
        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          class="message-wrapper"
          :class="{'user-wrapper': message.type === 'user', 'ai-wrapper': message.type === 'ai'}"
        >
          <div class="message-avatar" v-if="message.type === 'ai'">
            <div class="ai-avatar">R</div>
          </div>
          <div class="message" :class="message.type + '-message'">
            <div v-if="message.type === 'ai'" v-html="renderMarkdown(message.content)"></div>
            <div v-else>{{ message.content }}</div>
          </div>
        </div>
      </div>
      
      <div class="loading" v-if="loading">
        <div class="spinner"></div>
        <p>正在思考中...</p>
      </div>
      
      <div class="input-wrapper">
        <div class="kb-toggle">
          <label>
            <input type="checkbox" v-model="useKnowledgeBase" />
            <span class="toggle-label">使用知识库</span>
          </label>
          <button class="kb-manage-btn" @click="showKbPanel = true">知识库管理</button>
        </div>
        
        <div class="input-container">
          <input 
            type="text" 
            v-model="question" 
            @keyup.enter="sendQuestion"
            placeholder="请输入您的问题..." 
            :disabled="loading"
          >
          <button @click="sendQuestion" :disabled="loading">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import axios from 'axios'
import MarkdownIt from 'markdown-it'

// 初始化markdown解析器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
})

// 响应式状态
const question = ref('')
const messages = ref([
  { content: '你好呀！很高兴为你服务，有什么可以帮你的吗？ 😊', type: 'ai' }
])
const loading = ref(false)
const chatMessages = ref(null)

// 知识库相关状态
const useKnowledgeBase = ref(true)
const showKbPanel = ref(false)
const kbStatus = ref({
  active: false,
  document_count: 0,
  documents: []
})
const selectedFile = ref(null)
const uploading = ref(false)
const indexing = ref(false)
const fileInput = ref(null)

// 渲染Markdown
function renderMarkdown(text) {
  return md.render(text)
}

// 发送问题方法
async function sendQuestion() {
  const questionText = question.value.trim()
  if (!questionText) return
  
  // 添加用户问题到消息列表
  messages.value.push({ content: questionText, type: 'user' })
  question.value = ''
  loading.value = true
  
  try {
    // 调用API
    const response = await axios.post('/api/ask', { 
      question: questionText,
      use_knowledge_base: useKnowledgeBase.value
    })
    
    // 添加AI回答到消息列表
    messages.value.push({ content: response.data.answer, type: 'ai' })
  } catch (error) {
    console.error('Error:', error)
    let errorMessage = '发生错误，请稍后再试'
    
    if (error.response && error.response.data && error.response.data.error) {
      errorMessage = '错误: ' + error.response.data.error
    }
    
    messages.value.push({ content: errorMessage, type: 'ai' })
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

// 滚动到底部方法
function scrollToBottom() {
  if (chatMessages.value) {
    chatMessages.value.scrollTop = chatMessages.value.scrollHeight
  }
}

// 处理文件选择
function handleFileSelected(event) {
  const files = event.target.files
  if (files.length > 0) {
    selectedFile.value = files[0]
  } else {
    selectedFile.value = null
  }
}

// 上传文档
async function uploadDocument() {
  if (!selectedFile.value) return
  
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  
  try {
    uploading.value = true
    const response = await axios.post('/api/upload_document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    // 上传成功
    messages.value.push({ 
      content: `文档上传成功: ${response.data.message}`, 
      type: 'ai' 
    })
    
    // 清空选择的文件
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    
    // 刷新知识库状态
    fetchKnowledgeBaseStatus()
  } catch (error) {
    console.error('Error uploading document:', error)
    let errorMessage = '上传文档失败，请稍后再试'
    
    if (error.response && error.response.data && error.response.data.error) {
      errorMessage = '上传错误: ' + error.response.data.error
    }
    
    messages.value.push({ content: errorMessage, type: 'ai' })
  } finally {
    uploading.value = false
    await nextTick()
    scrollToBottom()
  }
}

// 重建索引
async function rebuildIndex() {
  try {
    indexing.value = true
    const response = await axios.post('/api/create_index')
    
    // 索引创建成功
    messages.value.push({ 
      content: `索引创建成功: ${response.data.message}`, 
      type: 'ai' 
    })
    
    // 刷新知识库状态
    fetchKnowledgeBaseStatus()
  } catch (error) {
    console.error('Error rebuilding index:', error)
    let errorMessage = '索引创建失败，请稍后再试'
    
    if (error.response && error.response.data && error.response.data.error) {
      errorMessage = '索引错误: ' + error.response.data.error
    }
    
    messages.value.push({ content: errorMessage, type: 'ai' })
  } finally {
    indexing.value = false
    await nextTick()
    scrollToBottom()
  }
}

// 获取知识库状态
async function fetchKnowledgeBaseStatus() {
  try {
    const response = await axios.get('/api/knowledge_base_status')
    kbStatus.value = response.data
  } catch (error) {
    console.error('Error fetching knowledge base status:', error)
  }
}

// 组件挂载时获取知识库状态
onMounted(() => {
  fetchKnowledgeBaseStatus()
})
</script>

<style>
body {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  line-height: 1.6;
  color: #333;
  margin: 0;
  padding: 0;
  background-color: #f7f7f7;
}

.app-container {
  max-width: 1000px;
  margin: 0 auto;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  text-align: center;
  padding: 15px 0;
  border-bottom: 1px solid #eaeaea;
}

h1 {
  font-size: 2rem;
  font-weight: bold;
  margin: 0;
  color: #222;
}

.chat-container {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin: 20px;
  overflow: hidden;
  position: relative;
}

.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 10px;
  margin-bottom: 20px;
}

.message-wrapper {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
}

.user-wrapper {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  margin: 0 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.ai-avatar {
  background-color: #4285f4;
  color: white;
}

.message {
  padding: 12px 16px;
  border-radius: 10px;
  max-width: 80%;
}

.user-message {
  background-color: #f0f9ff;
  margin-right: 10px;
  border: 1px solid #e4f2ff;
  text-align: right;
}

.ai-message {
  background-color: #f9f9f9;
  margin-left: 10px;
  border: 1px solid #f0f0f0;
}

/* Markdown样式 */
.ai-message h1, 
.ai-message h2,
.ai-message h3 {
  margin-top: 16px;
  margin-bottom: 8px;
  font-weight: 600;
}

.ai-message h1 {
  font-size: 1.4em;
  padding-bottom: 4px;
  border-bottom: 1px solid #eaecef;
}

.ai-message h2 {
  font-size: 1.2em;
}

.ai-message h3 {
  font-size: 1.1em;
}

.ai-message ul, 
.ai-message ol {
  padding-left: 20px;
  margin-bottom: 16px;
}

.ai-message code {
  background-color: rgba(27,31,35,0.05);
  border-radius: 3px;
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 85%;
  padding: 0.2em 0.4em;
}

.ai-message pre {
  background-color: #f6f8fa;
  border-radius: 3px;
  padding: 16px;
  overflow: auto;
  margin-bottom: 16px;
}

.ai-message blockquote {
  border-left: 4px solid #dfe2e5;
  color: #6a737d;
  padding: 0 16px;
  margin: 0 0 16px 0;
}

.ai-message p {
  margin-bottom: 16px;
}

.ai-message strong {
  font-weight: 600;
}

.ai-message em {
  font-style: italic;
}

.input-wrapper {
  margin-top: auto;
  border-top: 1px solid #eaeaea;
  padding-top: 15px;
}

.kb-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.toggle-label {
  margin-left: 8px;
}

.kb-manage-btn {
  background-color: #f1f1f1;
  color: #333;
  border: 1px solid #ddd;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 14px;
}

.input-container {
  display: flex;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 20px;
  overflow: hidden;
  padding: 5px;
}

input[type="text"] {
  flex-grow: 1;
  padding: 10px 15px;
  border: none;
  outline: none;
  font-size: 16px;
}

button {
  background-color: #4285f4;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

button:hover {
  background-color: #3367d6;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  margin: 10px 0;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 2s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 知识库面板样式 */
.knowledge-base-panel {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 350px;
  background-color: white;
  border-left: 1px solid #eaeaea;
  box-shadow: -2px 0 10px rgba(0,0,0,0.1);
  z-index: 10;
  overflow-y: auto;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.kb-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #eaeaea;
}

.kb-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
}

.close-btn:hover {
  color: #333;
}

.kb-content {
  padding: 16px;
}

.kb-status {
  margin-bottom: 16px;
}

.status-indicator {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #ccc;
  margin-right: 8px;
}

.status-indicator.active {
  background-color: #4CAF50;
}

.kb-documents {
  margin-bottom: 16px;
}

.kb-documents ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.kb-documents li {
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
}

.kb-upload {
  margin-bottom: 16px;
}

.kb-upload input[type="file"] {
  margin: 8px 0;
  width: 100%;
}

.kb-actions {
  margin-top: 16px;
  text-align: center;
}

.kb-actions button {
  width: 100%;
}
</style> 