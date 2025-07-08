#!/usr/bin/python3
# -- coding: utf-8 --
"""
需要安装依赖：
pip install pycryptodome

如果安装依赖pycryptodome出错时，请先在linux中安装gcc、python3-dev、libc-dev三个依赖

"""

import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

PUBLIC_KEY_BASE64 = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDc+CZK9bBA9IU+gZUOc6FUGu7yO9WpTNB0PzmgFBh96Mg1WrovD1oqZ+eIF4LjvxKXGOdI79JRdve9NPhQo07+uqGQgE4imwNnRx7PFtCRryiIEcUoavuNtuRVoBAm6qdB0SrctgaqGfLgKvZHOnwTjyNqjBUxzMeQlEC2czEMSwIDAQAB"
DEFAULT_SPLIT = "#PART#"
MAX_BLOCK_SIZE = 117

def rsa_encrypt(plaintext, public_key_base64):
    # 将Base64公钥解码为二进制
    der_data = base64.b64decode(public_key_base64)
    # 导入公钥
    public_key = RSA.importKey(der_data)
    cipher = PKCS1_v1_5.new(public_key)
    
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')
        
    # 如果不需要分块
    if len(plaintext) <= MAX_BLOCK_SIZE:
        return cipher.encrypt(plaintext)
    
    # 分块加密
    encrypted_blocks = []
    for i in range(0, len(plaintext), MAX_BLOCK_SIZE):
        block = plaintext[i:i + MAX_BLOCK_SIZE]
        encrypted_block = cipher.encrypt(block)
        if i > 0:
            # 在第一个块之后的分块前加入分隔符
            encrypted_blocks.append(DEFAULT_SPLIT.encode('utf-8'))
        encrypted_blocks.append(encrypted_block)
    
    return b''.join(encrypted_blocks)

def mobile_encrypt(data):
    encrypted_bytes = rsa_encrypt(data, PUBLIC_KEY_BASE64)
    return base64.b64encode(encrypted_bytes).decode('utf-8').replace('\n', '')

def password_encrypt(password, random_str="000000"):
    combined = password + random_str
    return mobile_encrypt(combined)

if __name__ == "__main__":
    password = "testPassword"
    encrypted_password = password_encrypt(password)
    print("Encrypted Password:", encrypted_password)
