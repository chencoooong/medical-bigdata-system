"""Kafka 数据生产者

用于将医疗数据推送到 Kafka，供下游系统消费。
"""

import json
import logging
from typing import Dict, Any
from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class MedicalKafkaProducer:
    """医疗数据 Kafka 生产者
    
    负责将医疗数据推送到 Kafka 主题。
    """
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        """初始化 Kafka 生产者
        
        Args:
            bootstrap_servers: Kafka 服务器地址
        """
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self._initialize_producer()
    
    def _initialize_producer(self) -> None:
        """初始化 Kafka 生产者"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3
            )
            logger.info(f"Kafka producer initialized: {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
    
    def send_patient_data(self, data: Dict[str, Any]) -> bool:
        """发送患者基本信息
        
        Args:
            data: 患者数据
        
        Returns:
            发送是否成功
        """
        return self._send_to_topic('patient_data', data)
    
    def send_lab_results(self, data: Dict[str, Any]) -> bool:
        """发送检验结果
        
        Args:
            data: 检验结果数据
        
        Returns:
            发送是否成功
        """
        return self._send_to_topic('lab_results', data)
    
    def _send_to_topic(self, topic: str, data: Dict[str, Any]) -> bool:
        """发送数据到指定主题
        
        Args:
            topic: Kafka 主题
            data: 数据内容
        
        Returns:
            发送是否成功
        """
        if not self.producer:
            logger.error("Kafka producer not initialized")
            return False
        
        try:
            future = self.producer.send(topic, value=data)
            record_metadata = future.get(timeout=10)
            logger.debug(f"Sent message to topic {record_metadata.topic}")
            return True
        except KafkaError as e:
            logger.error(f"Failed to send message to topic {topic}: {e}")
            return False
    
    def close(self) -> None:
        """关闭 Kafka 生产者"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")
