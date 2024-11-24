import logging
import sys
from typing import Optional

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取logger实例"""
    logger = logging.getLogger(name or __name__)

    if not logger.handlers:
        # 创建文件处理器，将日志写入文件
        file_handler = logging.FileHandler('rag_system.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)

        # 创建控制台处理器，但只输出ERROR级别以上的日志
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        console_handler.setLevel(logging.ERROR)
        logger.addHandler(console_handler)

        logger.setLevel(logging.INFO)

    return logger