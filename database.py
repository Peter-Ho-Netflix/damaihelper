from sqlmodel import SQLModel, Field, create_engine, Session, Relationship
from typing import Optional, List, Dict, Any
import os
import urllib.parse
from datetime import datetime

# 尝试从.env文件加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("成功从.env文件加载环境变量")
except ImportError:
    print("未安装python-dotenv库，将直接使用系统环境变量")

# 数据库连接配置类
class DatabaseConfig:
    def __init__(self):
        # 优先从环境变量获取数据库URL，支持云服务器部署
        self.db_url = os.getenv("DATABASE_URL")
        # 如果环境变量未设置，使用本地默认配置
        if not self.db_url:
            # 本地开发环境的默认配置
            db_user = os.getenv("DB_USER", "postgres")
            db_password = os.getenv("DB_PASSWORD", "password")
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME", "damaihelper")
            
            # 构建连接URL
            self.db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            print(f"使用本地数据库配置: {db_user}@{db_host}:{db_port}/{db_name}")
        else:
            print(f"使用DATABASE_URL连接数据库")

# 数据库连接管理
class Database:
    _instance = None
    _engine = None
    _session = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        config = DatabaseConfig()
        print(f"连接到数据库: {self._obfuscate_password(config.db_url)}")
        
        # 创建数据库引擎
        self._engine = create_engine(
            config.db_url,
            echo=os.getenv("DB_ECHO", "False").lower() == "true",
            connect_args={}
        )

    def _obfuscate_password(self, url: str) -> str:
        """隐藏URL中的密码，用于安全日志记录"""
        parsed = urllib.parse.urlparse(url)
        if parsed.netloc and ':' in parsed.netloc and '@' in parsed.netloc:
            user_pass, host_port = parsed.netloc.split('@', 1)
            user, _ = user_pass.split(':', 1)
            obfuscated_netloc = f"{user}:********@{host_port}"
            return url.replace(parsed.netloc, obfuscated_netloc)
        return url

    def get_engine(self):
        return self._engine

    def get_session(self):
        if self._session is None:
            self._session = Session(self._engine)
        return self._session

    def close(self):
        if self._session:
            self._session.close()
            self._session = None

# 数据库模型定义
# 用户/账户模型
class UserAccount(SQLModel, table=True):
    __tablename__ = "user_accounts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: str = Field(index=True, unique=True, description="账户唯一标识")
    username: str = Field(description="用户名/账号")
    password: str = Field(description="密码")  # 实际应用中应加密存储
    platform: str = Field(description="平台类型: damai, taopiaopiao等")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    is_active: bool = Field(default=True)
    
    # 与任务的关系
    tasks: List["TicketTask"] = Relationship(back_populates="account")

# 抢票任务模型
class TicketTask(SQLModel, table=True):
    __tablename__ = "ticket_tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: str = Field(index=True, unique=True, description="任务唯一标识")
    account_id: Optional[int] = Field(foreign_key="user_accounts.id", description="关联的账户ID")
    ticket_url: str = Field(description="购票页面URL")
    session_id: Optional[str] = Field(description="场次ID")
    ticket_type: Optional[str] = Field(description="票档类型")
    quantity: int = Field(default=1, description="购买数量")
    retry_interval: int = Field(default=5, description="重试间隔(秒)")
    auto_buy_time: Optional[str] = Field(description="自动购买时间")
    status: str = Field(default="pending", description="任务状态: pending, started, processing, completed, failed")
    progress: int = Field(default=0, description="任务进度")
    message: Optional[str] = Field(description="状态消息")
    result: Optional[Dict[str, Any]] = Field(sa_column_type="JSONB", description="任务结果")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # 与账户的关系
    account: Optional[UserAccount] = Relationship(back_populates="tasks")

# 代理IP模型
class ProxyIP(SQLModel, table=True):
    __tablename__ = "proxy_ips"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    ip: str = Field(description="代理IP地址")
    port: str = Field(description="代理端口")
    protocol: str = Field(default="http", description="代理协议")
    country: Optional[str] = Field(description="国家")
    city: Optional[str] = Field(description="城市")
    is_active: bool = Field(default=True, description="是否可用")
    last_checked: Optional[datetime] = Field(description="最后检查时间")
    response_time: Optional[float] = Field(description="响应时间(毫秒)")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})

# 日志模型
class TaskLog(SQLModel, table=True):
    __tablename__ = "task_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(foreign_key="ticket_tasks.id", description="关联的任务ID")
    log_level: str = Field(description="日志级别: info, warning, error")
    message: str = Field(description="日志消息")
    details: Optional[Dict[str, Any]] = Field(sa_column_type="JSONB", description="详细信息")
    created_at: datetime = Field(default_factory=datetime.now)

# 数据库初始化函数
def init_db():
    """初始化数据库，创建所有表"""
    db = Database.get_instance()
    engine = db.get_engine()
    SQLModel.metadata.create_all(engine)
    print("数据库表已创建完成")

# 数据库会话依赖
def get_db_session():
    """获取数据库会话，用于FastAPI依赖注入"""
    db = Database.get_instance()
    session = db.get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# 示例：保存任务到数据库
def save_task_to_db(task_id: str, request_data: Dict, status: str = "pending", progress: int = 0, message: str = ""):
    db = Database.get_instance()
    session = db.get_session()
    
    try:
        # 检查是否存在关联的用户账户
        account_id = None
        if request_data.get("accounts") and len(request_data["accounts"]) > 0:
            first_account = request_data["accounts"][0]
            # 查找或创建用户账户
            user_account = session.query(UserAccount).filter_by(account_id=first_account.get("id")).first()
            if not user_account:
                user_account = UserAccount(
                    account_id=first_account.get("id", "unknown"),
                    username=first_account.get("username", ""),
                    password=first_account.get("password", ""),
                    platform=first_account.get("platform", "damai")
                )
                session.add(user_account)
                session.commit()
            account_id = user_account.id
        
        # 创建任务记录
        ticket_task = TicketTask(
            task_id=task_id,
            account_id=account_id,
            ticket_url=request_data.get("ticket_settings", {}).get("url", ""),
            session_id=request_data.get("ticket_settings", {}).get("session_id"),
            ticket_type=request_data.get("ticket_settings", {}).get("ticket_type"),
            quantity=request_data.get("ticket_settings", {}).get("quantity", 1),
            retry_interval=request_data.get("ticket_settings", {}).get("retry_interval", 5),
            auto_buy_time=request_data.get("ticket_settings", {}).get("auto_buy_time"),
            status=status,
            progress=progress,
            message=message
        )
        
        session.add(ticket_task)
        session.commit()
        print(f"任务已保存到数据库: {task_id}")
        return ticket_task
    except Exception as e:
        session.rollback()
        print(f"保存任务到数据库失败: {str(e)}")
        raise e
    finally:
        session.close()

# 示例：更新任务状态
def update_task_in_db(task_id: str, status: str, progress: int, message: str, result: Optional[Dict] = None):
    db = Database.get_instance()
    session = db.get_session()
    
    try:
        task = session.query(TicketTask).filter_by(task_id=task_id).first()
        if task:
            task.status = status
            task.progress = progress
            task.message = message
            task.result = result
            session.commit()
            print(f"任务状态已更新: {task_id}, 状态: {status}")
        else:
            print(f"未找到任务: {task_id}")
    except Exception as e:
        session.rollback()
        print(f"更新任务状态失败: {str(e)}")
        raise e
    finally:
        session.close()