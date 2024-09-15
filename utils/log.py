import logging
from datetime import datetime

class CustomLogger:
    def __init__(self, log_filename):
        """
        初始化日志记录器，并设置日志文件的路径。
        
        :param log_filename: 日志文件的完整路径
        """
        self.logger = logging.getLogger(log_filename)
        self.logger.setLevel(logging.INFO)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)
        
        # 创建日志格式化器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # 添加处理器到日志记录器
        self.logger.addHandler(file_handler)
    
    def log_info(self, message):
        """
        记录一条信息级别的日志。
        
        :param message: 要记录的消息
        """
        self.logger.info(message)
    
    def log_error(self, message):
        """
        记录一条错误级别的日志。
        
        :param message: 要记录的消息
        """
        self.logger.error(message)
    
    def log_debug(self, message):
        """
        记录一条调试级别的日志。
        
        :param message: 要记录的消息
        """
        self.logger.debug(message)
    
    def log_warning(self, message):
        """
        记录一条警告级别的日志。
        
        :param message: 要记录的消息
        """
        self.logger.warning(message)
    
    def log_critical(self, message):
        """
        记录一条严重级别的日志。
        
        :param message: 要记录的消息
        """
        self.logger.critical(message)