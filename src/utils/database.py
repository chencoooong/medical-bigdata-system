"""数据库管理工具

提供数据库连接、查询等功能。
"""

import logging
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理类
    
    负责数据库连接、事务管理等。
    """
    
    def __init__(self, host: str, port: int, database: str,
                 user: str, password: str):
        """初始化数据库管理器
        
        Args:
            host: 数据库主机
            port: 数据库端口
            database: 数据库名称
            user: 数据库用户
            password: 数据库密码
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
    
    def connect(self) -> bool:
        """连接到数据库
        
        Returns:
            连接是否成功
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info(f"Database connected: {self.database}")
            return True
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            return False
    
    def disconnect(self) -> None:
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("Database disconnected")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Any]:
        """执行查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
        
        Returns:
            查询结果
        """
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return [dict(row) for row in results]
        except psycopg2.Error as e:
            logger.error(f"Query execution error: {e}")
            return []
