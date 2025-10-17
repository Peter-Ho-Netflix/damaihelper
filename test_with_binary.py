#!/usr/bin/env python3
"""
使用psycopg2-binary的数据库连接测试脚本
"""
import psycopg2
import sys
import os

print(f"Python版本: {sys.version}")
print(f"psycopg2模块: {psycopg2.__name__}")
print(f"系统默认编码: {sys.getdefaultencoding()}")

# 数据库连接参数
db_user = "postgres"
db_password = "postgres"
db_host = "localhost"
db_port = "5432"
db_name = "damaihelper"

print(f"\n尝试连接到PostgreSQL 17服务器...")

# 首先尝试连接到默认的postgres数据库检查连接性
try:
    print("步骤1: 尝试连接到默认的postgres数据库")
    conn_default = psycopg2.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        dbname="postgres"
    )
    print("✅ 成功连接到默认postgres数据库!")
    
    # 检查damaihelper数据库是否存在
    print("\n步骤2: 检查damaihelper数据库是否存在")
    with conn_default.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cur.fetchone() is not None
        if exists:
            print(f"✅ {db_name}数据库已存在")
        else:
            print(f"❌ {db_name}数据库不存在，需要创建")
            # 尝试创建数据库
            try:
                print("尝试创建damaihelper数据库...")
                cur.execute(f"CREATE DATABASE {db_name} ENCODING 'UTF8'")
                print(f"✅ 成功创建{db_name}数据库")
            except Exception as e:
                print(f"❌ 创建数据库失败: {str(e)}")
    
    conn_default.close()
    
    # 如果数据库存在或已创建，尝试连接到damaihelper数据库
    if exists or ('exists' in locals() and not exists):
        print("\n步骤3: 尝试连接到damaihelper数据库")
        try:
            conn_damai = psycopg2.connect(
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
                dbname=db_name
            )
            print(f"✅ 成功连接到{db_name}数据库!")
            
            # 获取数据库编码设置
            with conn_damai.cursor() as cur:
                cur.execute("SHOW server_encoding")
                encoding = cur.fetchone()[0]
                print(f"数据库服务编码: {encoding}")
                
                cur.execute("SHOW client_encoding")
                client_encoding = cur.fetchone()[0]
                print(f"客户端编码: {client_encoding}")
            
            conn_damai.close()
            print("✅ 数据库连接测试完成!")
        except Exception as e:
            print(f"❌ 连接到{db_name}数据库失败: {str(e)}")
            import traceback
            print(f"错误详情:\n{traceback.format_exc()}")
            
except Exception as e:
    print(f"❌ 连接到默认postgres数据库失败: {str(e)}")
    import traceback
    print(f"错误详情:\n{traceback.format_exc()}")

print("\n=== 最终建议 ===")
print("1. 确认PostgreSQL 17服务正在运行")
print("2. 如果密码包含非ASCII字符，请修改为纯ASCII字符")
print("3. 检查pg_hba.conf文件，确保允许本地连接")
print("4. 尝试在命令行中使用以下命令连接:\n   psql -U postgres -d postgres")
print("5. 如果问题依然存在，可能需要重新安装PostgreSQL或检查系统编码设置")