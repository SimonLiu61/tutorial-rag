# generator.py
from typing import List
from langchain.schema import Document, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback

from config import RAGConfig
from logger import get_logger

logger = get_logger(__name__)

class ResponseGenerator:
    """响应生成类"""
    def __init__(self, config: RAGConfig):
        self.config = config
        self.llm = ChatOpenAI(
            model_name=config.model_name,
            temperature=config.temperature
        )

    def generate_response(self, query: str, contexts: List[Document]) -> str:
        """生成回答"""
        system_prompt = """你是一个专业的计算机网络助教。
        你的任务是基于提供的上下文信息回答学生的问题。
        请保持回答的专业性和准确性。
        如果问题超出上下文范围，请明确指出。
        如果可能，在回答中引用具体的课程内容。
        """

        context_str = "\n\n".join([doc.page_content for doc in contexts])
        logger.info(f"上下文长度: {len(context_str)} 字符")

        human_prompt = f"""
        基于以下课程资料回答问题:
        
        {context_str}
        
        问题: {query}
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]

        with get_openai_callback() as cb:
            response = self.llm(messages)
            logger.info(f"Token 使用情况 - Prompt: {cb.prompt_tokens}, "
                       f"Completion: {cb.completion_tokens}, "
                       f"Cost: ${cb.total_cost}")

        return response.content
