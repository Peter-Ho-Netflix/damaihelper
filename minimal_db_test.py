#!/usr/bin/env python3
"""
最小化的数据库连接测试脚本
仅使用psycopg2进行基本连接测试
"""
import psycopg2
import sys
import os

# 打印系统信息
print(f"Python版本: {sys.version}")
print(f"psycopg2版本: {psycopg2.__version__}")
print(f"系统默认编码: {sys.getdefaultencoding()}")
print(f"环境编码: {os.environ.get('PYTHONIOENCODING', '未设置')}")

# 数据库连接参数 - 使用最简单的设置
db_user = "postgres"
db_password = "postgres"
db_host = "localhost"
db_port = "5432"
db_name = "damaihelper"

print(f"\n尝试连接到数据库 - 用户: {db_user}, 主机: {db_host}, 数据库: {db_name}")

# 尝试使用基本参数连接
try:
    # 逐个参数传递，避免URL构建时的编码问题
    conn = psycopg2.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        dbname=db_name
    )
    print("✅ 数据库连接成功!")
    
    # 获取数据库版本
    with conn.cursor() as cur:
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        print(f"数据库版本信息: {version[:100]}...")  # 只显示前100个字符
    
    conn.close()
    print("✅ 连接已关闭")
except Exception as e:
    print(f"❌ 数据库连接失败: {str(e)}")
    print(f"错误类型: {type(e).__name__}")
    import traceback
    print(f"错误详情:\n{traceback.format_exc()}")

print("\n=== 故障排查建议 ===")
print("1. 确认PostgreSQL服务是否正在运行")
print("2. 检查pg_hba.conf文件是否允许本地连接")
print("3. 确认postgresql.conf中的listen_addresses设置")
print("4. 尝试重置PostgreSQL服务")
print("5. 可能需要重新安装psycopg2或使用psycopg2-binary")
print("6. 检查数据库密码是否包含非ASCII字符")
print("7. 检查PostgreSQL服务器的编码设置")