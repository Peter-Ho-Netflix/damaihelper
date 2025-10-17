#!/usr/bin/env python3
"""
检查PostgreSQL服务状态并安装psycopg2-binary
"""
import os
import subprocess
import sys

print("=== 检查PostgreSQL服务状态 ===")

try:
    # 在Windows上检查PostgreSQL服务状态
    if sys.platform == 'win32':
        # 尝试使用sc命令检查服务状态
        result = subprocess.run(
            ['sc', 'query', 'postgresql-x64-16'],  # 假设是PostgreSQL 16版本
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print(f"PostgreSQL服务状态:\n{result.stdout}")
        else:
            # 尝试检查所有包含postgresql的服务
            print("尝试查找所有PostgreSQL相关服务...")
            services = subprocess.run(
                ['sc', 'query', 'type=', 'service', 'state=', 'all', '|', 'findstr', '/i', 'postgres'],
                shell=True,
                capture_output=True,
                text=True
            )
            if services.stdout:
                print(f"找到的PostgreSQL服务:\n{services.stdout}")
            else:
                print("未找到PostgreSQL服务。请确认PostgreSQL是否已安装。")
    else:
        # Linux/Mac检查方式
        result = subprocess.run(
            ['service', 'postgresql', 'status'],
            capture_output=True,
            text=True
        )
        print(f"PostgreSQL服务状态:\n{result.stdout}")
except Exception as e:
    print(f"检查PostgreSQL服务状态时出错: {str(e)}")

print("\n=== 尝试安装psycopg2-binary ===")

try:
    # 卸载现有的psycopg2
    print("尝试卸载现有的psycopg2...")
    subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', 'psycopg2'], check=False)
    
    # 安装psycopg2-binary
    print("安装psycopg2-binary...")
    subprocess.run(
        [sys.executable, '-m', 'pip', 'install', 'psycopg2-binary'],
        check=True,
        capture_output=True,
        text=True
    )
    print("✅ psycopg2-binary安装成功!")
except subprocess.CalledProcessError as e:
    print(f"❌ 安装psycopg2-binary失败: {e.stderr}")
except Exception as e:
    print(f"❌ 安装过程中出现错误: {str(e)}")

print("\n=== 建议操作 ===")
print("1. 确认PostgreSQL服务正在运行")
print("2. 确认'damaihelper'数据库已创建")
print("3. 确认postgres用户密码正确")
print("4. 如果问题依然存在，尝试重新安装PostgreSQL")
print("5. 尝试使用以下命令在命令行中直接连接数据库:\n   psql -U postgres -d damaihelper")