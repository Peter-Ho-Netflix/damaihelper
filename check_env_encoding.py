#!/usr/bin/env python3
"""
检查.env文件的内容和编码
"""
import os

# 检查.env文件是否存在
if os.path.exists('.env'):
    print("找到.env文件")
    
    # 尝试读取文件
    with open('.env', 'rb') as f:
        raw_data = f.read()
        
        # 直接显示前几个字节的十六进制表示
        print("文件前20个字节的十六进制表示:")
        hex_dump = ' '.join([f'{byte:02X}' for byte in raw_data[:20]])
        print(hex_dump)
        
        # 尝试以不同的编码读取文件
        print("\n尝试以不同编码解码文件内容:")
        
        # 尝试UTF-8
        try:
            content_utf8 = raw_data.decode('utf-8')
            print("UTF-8 解码成功:")
            print(content_utf8)
        except UnicodeDecodeError as e:
            print(f"UTF-8 解码失败: {e}")
            
        # 尝试GBK
        try:
            content_gbk = raw_data.decode('gbk')
            print("\nGBK 解码成功:")
            print(content_gbk)
        except UnicodeDecodeError as e:
            print(f"\nGBK 解码失败: {e}")
            
        # 尝试Latin-1 (不会失败，但可能显示乱码)
        try:
            content_latin1 = raw_data.decode('latin1')
            print("\nLatin-1 解码成功:")
            print(content_latin1)
        except UnicodeDecodeError as e:
            print(f"\nLatin-1 解码失败: {e}")
else:
    print("未找到.env文件")
    
# 检查系统环境变量
print("\n=== 系统环境变量检查 ===")
db_env_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'DATABASE_URL']
for var in db_env_vars:
    value = os.getenv(var)
    if value:
        masked_value = value if var != 'DB_PASSWORD' else '********'
        print(f"{var}: {masked_value}")
    else:
        print(f"{var}: 未设置")