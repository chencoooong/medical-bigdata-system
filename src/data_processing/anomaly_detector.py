"""异常检测模块

用于检测医疗数据中的异常和错误。
"""

import logging
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """异常检测工具
    
    使用统计方法和机器学习检测异常数据点。
    """
    
    def __init__(self, contamination: float = 0.05):
        """初始化异常检测器
        
        Args:
            contamination: 异常数据比例
        """
        self.contamination = contamination
        self.detector = IsolationForest(
            contamination=contamination,
            random_state=42
        )
    
    def detect_outliers_in_lab_results(self, df: pd.DataFrame,
                                       columns: List[str] = None) -> Tuple[pd.DataFrame, List[int]]:
        """检测检验结果中的异常值
        
        Args:
            df: 检验结果DataFrame
            columns: 要检测的列
        
        Returns:
            (清洁后的DataFrame, 异常数据的索引列表)
        """
        if columns is None:
            columns = ['result_value']
        
        # 选择存在的列
        valid_columns = [col for col in columns if col in df.columns]
        
        if not valid_columns:
            logger.warning("No valid columns for anomaly detection")
            return df, []
        
        # 提取数值数据
        X = df[valid_columns].copy()
        X = X.fillna(X.mean())
        
        # 检测异常
        predictions = self.detector.fit_predict(X)
        anomalies = np.where(predictions == -1)[0]
        
        logger.info(f"Detected {len(anomalies)} anomalies in lab results")
        
        # 标记异常
        df['is_anomaly'] = predictions == -1
        
        return df, anomalies.tolist()
    
    def detect_outliers_statistical(self, df: pd.DataFrame,
                                   column: str,
                                   std_threshold: float = 3.0) -> Tuple[pd.DataFrame, List[int]]:
        """使用标准差方法检测异常值
        
        Args:
            df: 输入DataFrame
            column: 要检测的列
            std_threshold: 标准差阈值
        
        Returns:
            (标记后的DataFrame, 异常数据的索引列表)
        """
        if column not in df.columns:
            logger.warning(f"Column {column} not found")
            return df, []
        
        mean = df[column].mean()
        std = df[column].std()
        
        # 计算Z分数
        df['z_score'] = np.abs((df[column] - mean) / std)
        
        # 识别异常（Z分数 > threshold）
        anomalies = df[df['z_score'] > std_threshold].index.tolist()
        
        logger.info(f"Detected {len(anomalies)} statistical anomalies in {column}")
        
        df['is_anomaly'] = df['z_score'] > std_threshold
        
        return df, anomalies
