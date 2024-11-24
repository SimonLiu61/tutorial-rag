import sys
from typing import Optional
import threading
from queue import Queue

class ConsoleUI:
    def __init__(self):
        self.output_queue = Queue()
        self.input_queue = Queue()
        self._stop_event = threading.Event()

    def clear_line(self):
        """清除当前行"""
        sys.stdout.write('\r\033[K')
        sys.stdout.flush()

    def print(self, message: str, end: str = '\n'):
        """打印消息"""
        self.clear_line()
        print(message, end=end)
        sys.stdout.flush()

    def input_prompt(self, prompt: str = "") -> str:
        """显示输入提示并获取用户输入"""
        self.clear_line()
        user_input = input(f"\n{prompt}")
        return user_input.strip()

    def display_response(self, response: str):
        """显示AI的响应"""
        self.print("\n回答:")
        self.print("-" * 80)
        self.print(response)
        self.print("-" * 80)