import os
import faiss
import numpy as np
import nltk
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader, UnstructuredMarkdownLoader

# 设置NLTK数据路径为项目根目录下的nltk_data文件夹
nltk_data_path = os.path.join(os.path.dirname(__file__), 'nltk_data')
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(nltk_data_path)

# 检查并下载必要NLTK数据
required_nltk_data = [
    'punkt', 
    'punkt_tab', 
    'averaged_perceptron_tagger',
    'averaged_perceptron_tagger_eng'  # 添加新的资源
]
for data in required_nltk_data:
    try:
        if data == 'punkt' or data == 'punkt_tab':
            nltk.data.find(f'tokenizers/{data}')
        else:
            nltk.data.find(f'taggers/{data}')
    except LookupError:
        print(f"正在下载NLTK数据包: {data}")
        nltk.download(data, download_dir=nltk_data_path)

from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
import pickle

class KnowledgeBase:
    def __init__(self, documents_dir="knowledge_documents"):
        """初始化知识库"""
        self.documents_dir = documents_dir
        self.embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        self.vector_store = None
        
        # 确保文档目录存在
        if not os.path.exists(documents_dir):
            os.makedirs(documents_dir)
            
        # 索引保存路径
        self.index_path = os.path.join(documents_dir, "faiss_index")
        self.documents_path = os.path.join(documents_dir, "documents.pkl")
        
        # 如果存在索引，加载它
        self.load_index()
    
    def load_documents(self):
        """加载文档目录中的所有文档"""
        documents = []
        
        for filename in os.listdir(self.documents_dir):
            file_path = os.path.join(self.documents_dir, filename)
            
            # 跳过索引文件和目录
            if os.path.isdir(file_path) or filename == "faiss_index" or filename == "documents.pkl":
                continue
                
            try:
                if filename.endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                    documents.extend(loader.load())
                elif filename.endswith('.txt'):
                    loader = TextLoader(file_path)
                    documents.extend(loader.load())
                elif filename.endswith('.docx') or filename.endswith('.doc'):
                    loader = UnstructuredWordDocumentLoader(file_path)
                    documents.extend(loader.load())
                elif filename.endswith('.md'):
                    loader = UnstructuredMarkdownLoader(file_path)
                    documents.extend(loader.load())
            except Exception as e:
                print(f"加载文档 {filename} 时出错: {str(e)}")
                
        return documents
    
    def create_index(self):
        """创建或更新向量存储索引"""
        documents = self.load_documents()
        
        if not documents:
            print("没有找到文档，无法创建索引")
            return False
            
        # 分割文档为块
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = text_splitter.split_documents(documents)
        
        # 创建向量存储
        self.vector_store = FAISS.from_documents(texts, self.embeddings)
        
        # 保存索引
        self.save_index()
        return True
    
    def save_index(self):
        """保存索引到文件"""
        if self.vector_store:
            # 保存FAISS索引
            self.vector_store.save_local(self.index_path)
            print(f"索引已保存到 {self.index_path}")
    
    def load_index(self):
        """从文件加载索引"""
        if os.path.exists(self.index_path):
            try:
                self.vector_store = FAISS.load_local(self.index_path, self.embeddings)
                print("成功加载现有知识库索引")
                return True
            except Exception as e:
                print(f"加载索引时出错: {str(e)}")
        return False
    
    def query(self, question, top_k=3):
        """根据问题查询相关文档"""
        if not self.vector_store:
            print("知识库索引未初始化，无法查询")
            return []
            
        # 添加关键词检测，只有包含特定前缀或明显需要知识库时才查询
        knowledge_keywords = ["知识库", "文档", "ONE Record", "部署指南"]  # 可根据需要添加更多关键词
        if not any(keyword.lower() in question.lower() for keyword in knowledge_keywords):
            return []
            
        try:
            similar_docs = self.vector_store.similarity_search(question, k=top_k)
            return similar_docs
        except Exception as e:
            print(f"查询知识库时出错: {str(e)}")
            return []
    
    def add_document(self, file_path):
        """添加新文档到知识库"""
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return False, "文件不存在"
            
        # 拷贝文件到知识库目录
        filename = os.path.basename(file_path)
        dest_path = os.path.join(self.documents_dir, filename)
        
        try:
            # 如果是支持的文件类型
            if (filename.endswith('.pdf') or filename.endswith('.txt') or 
                filename.endswith('.docx') or filename.endswith('.doc') or 
                filename.endswith('.md')):
                # 复制文件
                with open(file_path, 'rb') as src, open(dest_path, 'wb') as dst:
                    dst.write(src.read())
                    
                # 重新创建索引
                success = self.create_index()
                if success:
                    return True, f"文档 {filename} 已添加到知识库并索引"
                else:
                    return False, "索引创建失败"
            else:
                return False, "不支持的文件类型"
        except Exception as e:
            return False, f"添加文档时出错: {str(e)}"
    
    def get_context_for_question(self, question):
        """获取与问题相关的上下文内容"""
        docs = self.query(question)
        if not docs:
            return ""
            
        # 组合文档内容为上下文
        context = "\n\n".join([doc.page_content for doc in docs])
        return context

# 创建知识库单例
KB = KnowledgeBase()

# 用于测试
if __name__ == "__main__":
    KB.create_index()
    context = KB.get_context_for_question("测试问题")
    print(context)