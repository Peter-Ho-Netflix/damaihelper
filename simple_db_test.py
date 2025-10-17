#!/usr/bin/env python3
"""
简单的数据库连接测试脚本
不使用.env文件，直接硬编码连接参数
"""
import psycopg2
from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime

# 直接硬编码数据库连接参数
db_user = "postgres"
db_password = "postgres"
db_host = "localhost"
db_port = "5432"
db_name = "damaihelper"

# 构建连接URL
db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
print(f"尝试连接到数据库: {db_url}")

# 测试1: 使用psycopg2直接连接
print("\n=== 测试1: 使用psycopg2直接连接 ===")
try:
    conn = psycopg2.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        dbname=db_name
    )
    print("✅ psycopg2连接成功!")
    conn.close()
except Exception as e:
    print(f"❌ psycopg2连接失败: {str(e)}")
    import traceback
    print(f"错误详情: {traceback.format_exc()}")

# 测试2: 使用SQLModel连接
print("\n=== 测试2: 使用SQLModel连接 ===")
try:
    # 创建引擎
    engine = create_engine(db_url)
    
    # 测试连接
    with engine.connect() as conn:
        print("✅ SQLModel连接成功!")
        
        # 检查数据库版本
        result = conn.execute("SELECT version()")
        version = result.scalar()
        print(f"数据库版本: {version.split(' ')[1]}")
    
    print("✅ 数据库连接测试通过!")
except Exception as e:
    print(f"❌ SQLModel连接失败: {str(e)}")
    import traceback
    print(f"错误详情: {traceback.format_exc()}")

print("\n=== 故障排查建议 ===")
print("1. 确认PostgreSQL服务是否正在运行")
print("2. 检查pg_hba.conf文件是否允许本地连接")
print("3. 确认postgresql.conf中的listen_addresses设置")
print("4. 尝试重置PostgreSQL服务")
print("5. 可能需要重新安装psycopg2或使用psycopg2-binary")