# retriever.py
from typing import List, Optional
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from config import RAGConfig
from logger import get_logger

logger = get_logger(__name__)

class EnhancedRetriever:
    """增强检索类"""
    def __init__(self, config: RAGConfig):
        self.config = config
        self.embeddings = OpenAIEmbeddings(
            model=config.embedding_model,
            openai_api_key=config.openai_api_key
        )
        self.vector_store = None
        self.bm25_retriever = None
        self.ensemble_retriever = None
        self.all_documents = []

    def init_retrievers(self, documents: List[Document]):
        """初始化检索器"""
        logger.info("初始化检索器...")
        self.all_documents = documents

        # 初始化向量存储
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.config.persist_directory
        )

        # 初始化 BM25 检索器
        self.bm25_retriever = BM25Retriever.from_documents(documents)

        # 创建集成检索器
        vector_retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.config.top_k}
        )

        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[self.bm25_retriever, vector_retriever],
            weights=[0.3, 0.7]
        )

        logger.info("检索器初始化完成")

    def filter_documents_by_tutorial(self, documents: List[Document], tutorial_number: Optional[str]) -> List[Document]:
        """根据教程编号筛选文档"""
        if not tutorial_number:
            return documents

        return [
            doc for doc in documents
            if doc.metadata.get('tutorial_number', '').lower() == f"tutorial {tutorial_number}".lower()
        ]

    def retrieve(self, query: str, tutorial_number: Optional[str] = None) -> List[Document]:
        """执行检索，支持按教程筛选"""
        try:
            # 首先检查是否是特定教程的查询
            if tutorial_number:
                logger.info(f"正在检索 Tutorial {tutorial_number} 的内容...")
                # 首先过滤文档
                filtered_docs = self.filter_documents_by_tutorial(self.all_documents, tutorial_number)
                if not filtered_docs:
                    logger.warning(f"未找到 Tutorial {tutorial_number} 的文档")
                    return []

                # 在过滤后的文档中检索
                temp_vector_store = Chroma.from_documents(
                    documents=filtered_docs,
                    embedding=self.embeddings
                )
                documents = temp_vector_store.similarity_search(query, k=self.config.top_k)
            else:
                # 使用ensemble检索器检索所有文档
                documents = self.ensemble_retriever.get_relevant_documents(
                    query,
                    top_k=self.config.top_k
                )

            logger.info(f"检索到 {len(documents)} 个相关文档")
            return documents
        except Exception as e:
            logger.error(f"检索出错: {str(e)}")
            # 降级到基础向量检索
            return self.vector_store.similarity_search(
                query,
                k=self.config.top_k
            )

    def extract_tutorial_number_from_query(self, query: str) -> Optional[str]:
        """从查询中提取教程编号"""
        import re
        match = re.search(r'tutorial[- ]?(\d+)', query.lower())
        return match.group(1) if match else None