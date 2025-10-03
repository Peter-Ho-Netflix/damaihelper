#!/usr/bin/env python3
"""
数据库连接测试脚本
用于验证PostgreSQL数据库配置是否正确
"""

from sqlmodel import SQLModel, Field, create_engine, Session
import os
import urllib.parse
from datetime import datetime
import sys

def test_db_connection():
    """测试数据库连接和基本操作"""
    print("=== PostgreSQL数据库连接测试 ===")
    
    # 获取数据库URL
    db_url = os.getenv("DATABASE_URL")
    
    # 如果环境变量未设置，使用本地默认配置
    if not db_url:
        print("未找到DATABASE_URL环境变量，使用本地默认配置")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "password")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "damaihelper")
        
        # 构建连接URL
        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    # 隐藏密码显示
    def obfuscate_password(url):
        parsed = urllib.parse.urlparse(url)
        if parsed.netloc and ':' in parsed.netloc and '@' in parsed.netloc:
            user_pass, host_port = parsed.netloc.split('@', 1)
            user, _ = user_pass.split(':', 1)
            obfuscated_netloc = f"{user}:********@{host_port}"
            return url.replace(parsed.netloc, obfuscated_netloc)
        return url
    
    print(f"尝试连接到数据库: {obfuscate_password(db_url)}")
    
    try:
        # 创建引擎
        engine = create_engine(db_url)
        
        # 测试连接
        with engine.connect() as conn:
            print("✅ 数据库连接成功！")
            
            # 检查数据库版本
            result = conn.execute("SELECT version()")
            version = result.scalar()
            print(f"数据库版本: {version.split(' ')[1]}")
        
        # 定义测试模型
        class TestModel(SQLModel, table=True):
            __tablename__ = "test_table"
            id: int = Field(default=None, primary_key=True)
            message: str
            created_at: datetime = Field(default_factory=datetime.now)
        
        # 创建表
        print("创建测试表...")
        SQLModel.metadata.create_all(engine)
        
        # 添加测试数据
        print("插入测试数据...")
        with Session(engine) as session:
            test_record = TestModel(message="数据库连接测试成功！")
            session.add(test_record)
            session.commit()
            
            # 查询测试数据
            print("查询测试数据...")
            results = session.query(TestModel).all()
            for record in results:
                print(f"找到记录: ID={record.id}, 消息={record.message}, 创建时间={record.created_at}")
            
            # 删除测试数据
            print("清理测试数据...")
            session.query(TestModel).delete()
            session.commit()
        
        # 删除测试表
        print("删除测试表...")
        TestModel.__table__.drop(engine)
        
        print("✅ 数据库操作测试完成！")
        
        # 提供配置建议
        print("\n=== 配置建议 ===")
        print("1. 本地开发环境下，您可以设置以下环境变量来配置数据库：")
        print("   DB_USER=postgres")
        print("   DB_PASSWORD=your_password")
        print("   DB_HOST=localhost")
        print("   DB_PORT=5432")
        print("   DB_NAME=damaihelper")
        print("\n2. 云服务器环境下，推荐设置DATABASE_URL环境变量：")
        print("   DATABASE_URL=postgresql://username:password@host:port/database")
        print("\n3. 请参考README_DB.md文件获取详细配置说明。")
        
    except Exception as e:
        print(f"❌ 数据库操作失败: {str(e)}")
        print("\n=== 故障排查建议 ===")
        print("1. 请确认PostgreSQL服务是否正在运行")
        print("2. 检查数据库凭证（用户名和密码）是否正确")
        print("3. 确认数据库名称是否存在")
        print("4. 检查防火墙设置是否允许连接到PostgreSQL端口")
        print("5. 查看README_DB.md文件获取详细配置指南")
        sys.exit(1)
    
if __name__ == "__main__":
    test_db_connection()