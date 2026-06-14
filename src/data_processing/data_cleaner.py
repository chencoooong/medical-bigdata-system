"""数据清洗模块

用于清洗和预处理医疗数据。
"""

import logging
from typing import Dict
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataCleaner:
    """数据清洗工具
    
    负责处理缺失值、异常值、重复数据、格式转换等。
    """
    
    def __init__(self):
        """初始化数据清洗工具"""
        self.records_processed = 0
        self.records_cleaned = 0
    
    def clean_patient_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗患者数据
        
        Args:
            df: 患者数据DataFrame
        
        Returns:
            清洗后的DataFrame
        """
        logger.info(f"Starting to clean {len(df)} patient records")
        self.records_processed += len(df)
        
        # 移除重复患者
        df = df.drop_duplicates(subset=['patient_id'], keep='first')
        
        # 处理缺失值
        df = self._handle_missing_values(df)
        
        # 验证邮箱格式
        if 'email' in df.columns:
            df = df[df['email'].str.match(r'^[^@]+@[^@]+\.[^@]+$', na=False) | df['email'].isna()]
        
        # 转换日期格式
        date_columns = ['date_of_birth', 'created_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        self.records_cleaned += len(df)
        logger.info(f"Cleaned {len(df)} patient records")
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """处理缺失值
        
        Args:
            df: 输入DataFrame
        
        Returns:
            处理后的DataFrame
        """
        # 对于分类列，用 'Unknown' 填充
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            df[col] = df[col].fillna('Unknown')
        
        # 对于数值列，用中位数填充
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            df[col] = df[col].fillna(df[col].median())
        
        return df
    
    def get_statistics(self) -> Dict[str, int]:
        """获取清洗统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'total_processed': self.records_processed,
            'total_cleaned': self.records_cleaned,
        }
