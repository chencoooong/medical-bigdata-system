"""数据接入模块"""

from .his_connector import HISConnector
from .lis_connector import LISConnector
from .kafka_producer import MedicalKafkaProducer

__all__ = ['HISConnector', 'LISConnector', 'MedicalKafkaProducer']
