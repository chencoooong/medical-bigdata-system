"""HIS 系统数据接入器

HIS (Hospital Information System) 连接器用于从医院信息系统获取患者基本信息、
就诊记录、出院摘要等数据。
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class HISConnector:
    """HIS 系统连接器
    
    负责从 HIS 系统提取患者信息、就诊记录等数据。
    """
    
    def __init__(self, host: str, port: int, database: str, 
                 user: str, password: str):
        """初始化 HIS 连接器
        
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
        """连接到 HIS 数据库
        
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
            logger.info(f"Successfully connected to HIS database: {self.database}")
            return True
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to HIS database: {e}")
            return False
    
    def disconnect(self) -> None:
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from HIS database")
    
    def fetch_patients(self, limit: int = 1000, offset: int = 0) -> List[Dict]:
        """获取患者基本信息
        
        Args:
            limit: 返回记录数限制
            offset: 偏移量
        
        Returns:
            患者信息列表
        """
        if not self.connection:
            logger.error("Database connection not established")
            return []
        
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = f"""
                SELECT 
                    patient_id,
                    patient_name,
                    gender,
                    date_of_birth,
                    id_number,
                    phone_number,
                    email,
                    home_address,
                    blood_type,
                    created_at
                FROM patients
                ORDER BY patient_id
                LIMIT {limit} OFFSET {offset}
            """
            cursor.execute(query)
            patients = cursor.fetchall()
            cursor.close()
            
            logger.info(f"Fetched {len(patients)} patients from HIS")
            return [dict(p) for p in patients]
        except psycopg2.Error as e:
            logger.error(f"Error fetching patients: {e}")
            return []
