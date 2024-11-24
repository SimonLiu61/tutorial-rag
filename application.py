# application.py
from typing import Optional
from config import RAGConfig
from document_processor import DocumentProcessor
from retriever import EnhancedRetriever
from generator import ResponseGenerator
from logger import get_logger
from ui import ConsoleUI

logger = get_logger(__name__)

class RAGApplication:
    """RAG 应用主类"""
    def __init__(self, config: RAGConfig):
        self.config = config
        self.doc_processor = DocumentProcessor(config)
        self.retriever = EnhancedRetriever(config)
        self.generator = ResponseGenerator(config)
        self.ui = ConsoleUI()

    def initialize(self):
        """初始化应用"""
        self.ui.print("正在初始化 RAG 应用...")

        # 加载文档
        documents = self.doc_processor.load_documents()

        # 初始化检索器
        self.retriever.init_retrievers(documents)

        self.ui.print("初始化完成！")

    def answer_question(self, query: str) -> str:
        """问答主接口"""
        try:
            self.ui.print("正在处理您的问题...")

            # 从查询中提取教程编号
            tutorial_number = self.retriever.extract_tutorial_number_from_query(query)

            # 检索相关文档
            if tutorial_number:
                self.ui.print(f"正在检索 Tutorial {tutorial_number} 的相关内容...")
                contexts = self.retriever.retrieve(query, tutorial_number)
                if not contexts:
                    return f"抱歉，未找到 Tutorial {tutorial_number} 的相关内容。"
            else:
                contexts = self.retriever.retrieve(query)

            if not contexts:
                return "抱歉，未找到相关内容。"
            
            # 生成回答
            response = self.generator.generate_response(query, contexts)
            
            return response
        except Exception as e:
            logger.error(f"处理问题时出错: {str(e)}")
            return f"抱歉，处理您的问题时出现错误: {str(e)}"