# document_processor.py
import os
import glob
from typing import List, Dict
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from config import RAGConfig
from logger import get_logger

logger = get_logger(__name__)

class DocumentProcessor:
    """改进的文档处理类"""
    def __init__(self, config: RAGConfig):
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=["\n\n", "\n", ".", "。", " ", ""]
        )
        self.documents_info: Dict[str, List[Document]] = {}  # 存储每个文档的chunks

    def extract_tutorial_number(self, filename: str) -> str:
        """从文件名提取教程编号"""
        import re
        match = re.search(r'Tutorial[- ](\d+)', filename, re.IGNORECASE)
        return f"Tutorial {match.group(1)}" if match else "Unknown"

    def load_documents(self) -> List[Document]:
        """加载并处理文档，增强元数据"""
        all_documents = []
        pdf_files = glob.glob(os.path.join(self.config.data_dir, "*.pdf"))

        if not pdf_files:
            raise FileNotFoundError(f"在 {self.config.data_dir} 目录下没有找到PDF文件")

        logger.info(f"找到 {len(pdf_files)} 个PDF文件")

        for pdf_path in pdf_files:
            try:
                filename = os.path.basename(pdf_path)
                tutorial_number = self.extract_tutorial_number(filename)
                logger.info(f"处理文件: {filename} ({tutorial_number})")

                loader = PyPDFLoader(pdf_path)
                docs = loader.load()

                # 增强每个文档块的元数据
                enhanced_docs = []
                for doc in docs:
                    doc.metadata.update({
                        'filename': filename,
                        'tutorial_number': tutorial_number,
                        'file_path': pdf_path,
                        'document_type': 'tutorial',
                    })
                    enhanced_docs.append(doc)

                chunks = self.text_splitter.split_documents(enhanced_docs)

                # 保存到文档信息字典
                self.documents_info[tutorial_number] = chunks
                all_documents.extend(chunks)

                logger.info(f"成功处理 {len(chunks)} 个文本块")
            except Exception as e:
                logger.error(f"处理 {pdf_path} 时出错: {str(e)}")
                continue

        return all_documents

    def get_tutorial_documents(self, tutorial_number: str) -> List[Document]:
        """获取特定教程的文档"""
        tutorial_key = f"Tutorial {tutorial_number}" if tutorial_number.isdigit() else tutorial_number
        return self.documents_info.get(tutorial_key, [])