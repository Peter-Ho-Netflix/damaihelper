#!/usr/bin/env python3
"""
使用autocommit模式创建数据库并测试连接
"""
import psycopg2
import sys
import os

print(f"Python版本: {sys.version}")
print(f"psycopg2模块: {psycopg2.__name__}")
print(f"系统默认编码: {sys.getdefaultencoding()}")
print(f"当前路径: {os.getcwd()}")

# 数据库连接参数
db_user = "postgres"
db_password = "postgres"
db_host = "localhost"
db_port = "5432"
db_name = "damaihelper"

print(f"\n尝试连接到PostgreSQL 17服务器...")

# 尝试连接到默认的postgres数据库并创建damaihelper数据库
try:
    print("步骤1: 使用autocommit模式连接到默认postgres数据库")
    # 先不指定数据库名连接
    conn = psycopg2.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    conn.autocommit = True  # 设置为autocommit模式
    print("✅ 成功连接到PostgreSQL服务器!")
    
    # 检查damaihelper数据库是否存在
    print("\n步骤2: 检查damaihelper数据库是否存在")
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cur.fetchone() is not None
        if exists:
            print(f"✅ {db_name}数据库已存在")
        else:
            print(f"❌ {db_name}数据库不存在，尝试创建...")
            try:
                cur.execute(f"CREATE DATABASE {db_name} TEMPLATE template0 ENCODING 'UTF8' LC_COLLATE 'C' LC_CTYPE 'C'")
                print(f"✅ 成功创建{db_name}数据库")
                exists = True
            except Exception as e:
                print(f"❌ 创建数据库失败: {str(e)}")
                import traceback
                print(f"错误详情:\n{traceback.format_exc()}")
    
    conn.close()
    
    # 如果数据库存在，尝试连接
    if exists:
        print("\n步骤3: 尝试连接到已创建的damaihelper数据库")
        try:
            # 设置客户端编码为UTF8
            conn_damai = psycopg2.connect(
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
                dbname=db_name,
                options='-c client_encoding=utf8'
            )
            print(f"✅ 成功连接到{db_name}数据库!")
            
            # 检查数据库编码设置
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
            
            # 尝试使用不同的连接方式
            print("\n尝试使用dsn字符串连接...")
            try:
                dsn = f"dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}"
                conn_dsn = psycopg2.connect(dsn)
                print("✅ 使用dsn字符串连接成功!")
                conn_dsn.close()
            except Exception as e_dsn:
                print(f"❌ 使用dsn字符串连接失败: {str(e_dsn)}")

except Exception as e:
    print(f"❌ 连接到PostgreSQL服务器失败: {str(e)}")
    import traceback
    print(f"错误详情:\n{traceback.format_exc()}")

print("\n=== 最终建议 ===")
print("1. 如果仍然遇到编码错误，可能是psycopg2与Python 3.12/PostgreSQL 17的兼容性问题")
print("2. 尝试降级到Python 3.11或使用更稳定的PostgreSQL版本")
print("3. 检查PostgreSQL的pg_hba.conf文件，确保本地连接设置正确")
print("4. 尝试在命令行中使用以下命令连接和创建数据库:\n   psql -U postgres\n   CREATE DATABASE damaihelper ENCODING 'UTF8';")
print("5. 如果问题依然存在，考虑使用其他数据库连接方式或ORM")