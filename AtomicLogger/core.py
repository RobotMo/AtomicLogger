import logging
from threading import Lock
import inspect
from uuid import uuid4
import sys


class ALogger():
    def __init__(self, src_logger: logging.Logger, block_name="ALoggerBlock", sep: str = "==" * 20) -> None:
        self._src_logger = src_logger
        self._name = src_logger.name
        self._formater = self._get_formater(src_logger)
        self._sep = sep
        self._block_name = block_name
        self._msg_list = []
        self._null_logger = self._get_null_logger(src_logger)


    def _get_null_logger(self, src_logger):
        null_logger = logging.getLogger(str(uuid4()))
        null_logger.setLevel(logging.DEBUG)
        null_logger.handlers.clear()
        null_logger.propagate = False
        for handler in src_logger.handlers:
            new_handle = self._clone_handler(handler)
            new_handle.setFormatter(logging.Formatter("%(message)s"))
            null_logger.addHandler(
                new_handle
            )
        return null_logger

    def __enter__(self):
        '''
        进入管理器，清空消息列表
        '''
        if self._msg_list:
            self._src_logger.warning(f"logger {self._name} has {len(self._msg_list)} messages in msg-list")
        self._src_logger.info(f"enter alogger {self._block_name}")
        self._msg_list = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        打印非空消息
        '''
        head = '\n' + self._sep + self._block_name + " BEGIN" + self._sep + '\n'
        tail = '\n' + self._sep + self._block_name + " END" + self._sep + '\n'
        msgs = '\n'.join(
                [msg for msg in self._msg_list if msg]
            )
        self._null_logger.debug(head + msgs + tail)

        return True

    def _get_formater(self, src_logger):
        '''
        获取src_logger中handler 的 formatter
        '''
        formatter = None
        for handler in src_logger.handlers:
            formatter = handler.formatter
            break

        
        if formatter is None:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        return formatter


    def format_massage(self, level:int, message:str, pathname="", lineno=0, func=None):
        """
        使用已有 logger 的格式配置，但只返回字符串不输出
        """
        # 创建记录
        record = logging.LogRecord(
            name=self._name,
            level=level,
            pathname=pathname,
            lineno=lineno,
            msg=message,
            args=(),
            exc_info=None,
            func=func
        )

        # 格式化
        return self._formater.format(record)
    
    def atom_error(self, msg: str):
        caller = inspect.stack()[1]
        record = self.format_massage(logging.ERROR, msg, caller.filename, caller.lineno, caller.function)

        self._msg_list.append(record)
    
    def atom_info(self, msg: str):
        caller = inspect.stack()[1]
        record = self.format_massage(logging.INFO, msg, caller.filename, caller.lineno, caller.function)

        self._msg_list.append(record)
    
    def atom_warning(self, msg: str):
        caller = inspect.stack()[1]
        record = self.format_massage(logging.WARNING, msg, caller.filename, caller.lineno, caller.function)

        self._msg_list.append(record)
    
    def atom_fatal(self, msg: str):
        caller = inspect.stack()[1]
        record = self.format_massage(logging.FATAL, msg, caller.filename, caller.lineno, caller.function)

        self._msg_list.append(record)
    
    def atom_debug(self, msg: str):
        caller = inspect.stack()[1]
        record = self.format_massage(logging.DEBUG, msg, caller.filename, caller.lineno, caller.function)

        self._msg_list.append(record)

    @staticmethod
    def setup_normal_logger(
        name,
        level: int = logging.INFO,
        log_file: str | None = None,
        format_string: str | None = None,
        datefmt: str = '%Y-%m-%d %H:%M:%S'
    ) -> logging.Logger:
        """
        创建一个自定义 logger
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 清除已有处理器（避免重复）
        logger.handlers.clear()
        
        # 默认格式
        if format_string is None:
            format_string = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        
        formatter = logging.Formatter(format_string, datefmt=datefmt)
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器（可选）
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            # 文件可以用不同格式
            file_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        # 不向父级传播
        logger.propagate = False
        
        return logger

    @staticmethod
    def _clone_handler(handler: logging.Handler) -> logging.Handler:
        """
        克隆一个 handler，保留配置但新建实例
        """
        # 根据类型创建新的 handler
        if isinstance(handler, logging.FileHandler):
            # 文件 handler：复制路径、模式、编码
            new_handler = logging.FileHandler(
                handler.baseFilename,
                mode=getattr(handler, 'mode', 'a'),
                encoding=getattr(handler, 'encoding', None)
            )
            
        elif isinstance(handler, logging.StreamHandler):
            # 流 handler：复制输出流
            stream = getattr(handler, 'stream', None)
            # 标准流特殊处理
            import sys
            if stream is sys.stdout:
                new_handler = logging.StreamHandler(sys.stdout)
            elif stream is sys.stderr:
                new_handler = logging.StreamHandler(sys.stderr)
            else:
                new_handler = logging.StreamHandler(stream)
                
        elif isinstance(handler, logging.handlers.RotatingFileHandler):
            new_handler = logging.handlers.RotatingFileHandler(
                handler.baseFilename,
                mode=getattr(handler, 'mode', 'a'),
                maxBytes=handler.maxBytes,
                backupCount=handler.backupCount,
                encoding=getattr(handler, 'encoding', None)
            )

        elif isinstance(handler, logging.handlers.TimedRotatingFileHandler):
            new_handler = logging.handlers.TimedRotatingFileHandler(
                handler.baseFilename,
                when=handler.when,
                interval=handler.interval,
                backupCount=handler.backupCount,
                encoding=getattr(handler, 'encoding', None)
            )
            
        elif isinstance(handler, logging.NullHandler):
            new_handler = logging.NullHandler()
        else:
            # 其他类型：尝试通用构造
            new_handler = handler.__class__()
        
        # 复制通用属性
        new_handler.setLevel(handler.level)
        
        # 复制 filters
        for f in handler.filters:
            new_handler.addFilter(f)
        
        return new_handler