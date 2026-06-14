"""数据加密工具"""

import logging
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64

logger = logging.getLogger(__name__)


class EncryptionManager:
    """数据加密管理器
    
    提供加密、解密、哈希等功能用于保护敏感数据。
    """
    
    def __init__(self, master_key: str):
        """初始化加密管理器
        
        Args:
            master_key: 主加密密钥
        """
        # 从主密钥生成 Fernet 密钥
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'medical_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """加密数据
        
        Args:
            data: 要加密的数据
        
        Returns:
            加密后的数据
        """
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return None
    
    def decrypt(self, encrypted_data: str) -> str:
        """解密数据
        
        Args:
            encrypted_data: 加密的数据
        
        Returns:
            解密后的数据
        """
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return None
    
    @staticmethod
    def hash_patient_id(patient_id: str) -> str:
        """对患者ID进行哈希（用于脱敏）
        
        Args:
            patient_id: 患者ID
        
        Returns:
            哈希值
        """
        return hashlib.sha256(patient_id.encode()).hexdigest()[:16]
    
    @staticmethod
    def mask_sensitive_data(data: str, visible_chars: int = 2) -> str:
        """掩码敏感数据
        
        Args:
            data: 敏感数据
            visible_chars: 可见字符数
        
        Returns:
            掩码后的数据
        """
        if len(data) <= visible_chars:
            return '*' * len(data)
        return data[:visible_chars] + '*' * (len(data) - visible_chars)
