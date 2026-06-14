"""LIS 系统数据接入器

LIS (Laboratory Information System) 连接器用于从实验室信息系统获取患者
检验结果、血象、生化指标等数据。
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class LISConnector:
    """LIS 系统连接器
    
    负责从 LIS 系统提取患者检验结果等数据。
    """
    
    def __init__(self, host: str, port: int, database: str,
                 user: str, password: str):
        """初始化 LIS 连接器
        
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
        """连接到 LIS 数据库
        
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
            logger.info(f"Successfully connected to LIS database: {self.database}")
            return True
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to LIS database: {e}")
            return False
    
    def disconnect(self) -> None:
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from LIS database")
    
    def fetch_lab_results(self, patient_id: str, 
                         days: int = 30) -> List[Dict]:
        """获取患者检验结果
        
        Args:
            patient_id: 患者ID
            days: 查询天数
        
        Returns:
            检验结果列表
        """
        if not self.connection:
            logger.error("Database connection not established")
            return []
        
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = """
                SELECT 
                    test_id,
                    patient_id,
                    test_date,
                    test_name,
                    test_code,
                    result_value,
                    unit,
                    reference_range,
                    abnormal_flag,
                    status
                FROM lab_tests
                WHERE patient_id = %s 
                AND test_date >= NOW() - INTERVAL '%s days'
                ORDER BY test_date DESC
            """
            cursor.execute(query, (patient_id, days))
            results = cursor.fetchall()
            cursor.close()
            
            logger.info(f"Fetched {len(results)} lab results for patient {patient_id}")
            return [dict(r) for r in results]
        except psycopg2.Error as e:
            logger.error(f"Error fetching lab results: {e}")
            return []
