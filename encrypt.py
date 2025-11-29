# encrypt.py

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib

def get_key(raw_key: str) -> bytes:
    """将明文密码转换为固定长度的 AES 密钥（32 字节）"""
    return hashlib.sha256(raw_key.encode()).digest()

def encrypt_text(text: str, raw_key: str) -> str:
    """使用 AES-CBC 模式加密文本"""
    key = get_key(raw_key)
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(text.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode()
    ct = base64.b64encode(ct_bytes).decode()
    return f"{iv}:{ct}"

def decrypt_text(encrypted: str, raw_key: str) -> str:
    """使用 AES-CBC 模式解密文本"""
    try:
        key = get_key(raw_key)
        iv, ct = encrypted.split(":")
        cipher = AES.new(key, AES.MODE_CBC, base64.b64decode(iv))
        pt = unpad(cipher.decrypt(base64.b64decode(ct)), AES.block_size)
        return pt.decode()
    except Exception:
        return "[解密失败]"
