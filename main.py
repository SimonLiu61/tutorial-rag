import os
from typing import Optional
from dotenv import load_dotenv
from config import RAGConfig
from application import RAGApplication
from logger import get_logger
from ui import ConsoleUI

logger = get_logger(__name__)

def main():
    load_dotenv()
    
    ui = ConsoleUI()
    
    # 配置检查
    if not os.path.exists("data"):
        ui.print("Error: 'data' 目录不存在")
        return

    # 获取 API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        ui.print("Error: OPENAI_API_KEY not found in environment variables")
        return

    # 初始化配置
    config = RAGConfig(
        openai_api_key=api_key
    )

    # 创建并初始化应用
    app = RAGApplication(config)
    app.initialize()

    # 交互式问答循环
    ui.print("\n开始问答会话，输入 'quit' 退出")
    ui.print("=" * 80)
    
    while True:
        query = ui.input_prompt("请输入您的问题: ")
        if query.lower() == 'quit':
            break

        response = app.answer_question(query)
        ui.display_response(response)
        ui.print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
