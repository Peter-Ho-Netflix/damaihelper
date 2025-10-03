# 大麦抢票助手 - 数据库配置指南

## 为什么需要数据库？

为抢票任务创建本地数据库有以下几个重要原因：

1. **任务持久化**: 保存任务历史记录和执行结果，即使服务重启也不会丢失
2. **多设备协作**: 支持多前端设备同时访问和管理任务
3. **数据分析**: 对历史抢票数据进行统计和分析，优化抢票策略
4. **用户管理**: 集中管理多个大麦账号和配置
5. **云部署支持**: 为未来部署到云服务器提供数据持久化能力

## PostgreSQL数据库配置

### 本地开发环境

1. **安装PostgreSQL**
   - Windows: 从 [PostgreSQL官网](https://www.postgresql.org/download/windows/) 下载安装程序
   - 或通过`winget` 安装 `winget install PostgreSQL.PostgreSQL`
   - Ubuntu: `sudo apt install postgresql postgresql-contrib`
   - macOS: `brew install postgresql`
   - 或从 [PostgreSQL官网](https://www.postgresql.org/download/macosx/) 下载安装程序
   可选：安装MySQL
   - Windows: 从 [MySQL官网](https://dev.mysql.com/downloads/windows/installer/) 下载安装程序
      - 或通过`winget` 安装 `winget install MySQL.MySQL`
   - Ubuntu: `sudo apt install mysql-server`
   - macOS: `brew install mysql`
    - 或从 [MySQL官网](https://dev.mysql.com/downloads/mysql/) 下载安装程序

2. **创建数据库**
   ```sql
   -- 登录PostgreSQL
   psql -U postgres
   
   -- 创建数据库
   CREATE DATABASE damaihelper;
   
   -- 创建用户（可选）
   CREATE USER your_username WITH PASSWORD 'your_password';
   
   -- 授予权限
   GRANT ALL PRIVILEGES ON DATABASE damaihelper TO your_username;
   ```

3. **配置环境变量**

   项目支持通过以下三种方式配置数据库环境变量：

   **方式一：使用.env文件（推荐）**
   - 复制 `.env.example` 文件并重命名为 `.env`
   - 根据您的PostgreSQL配置修改 `.env` 文件中的值：
     ```env
     # 本地开发环境使用以下配置
     DB_USER=postgres
     DB_PASSWORD=your_password
     DB_HOST=localhost
     DB_PORT=5432
     DB_NAME=damaihelper
     
     # 数据库调试模式
     # DB_ECHO=true
     ```
   - 项目会自动从 `.env` 文件加载这些环境变量

   **方式二：系统环境变量**
   - Windows: 在系统环境变量中添加
     ```
     DB_USER=postgres
     DB_PASSWORD=your_password
     DB_HOST=localhost
     DB_PORT=5432
     DB_NAME=damaihelper
     ```
   - Ubuntu: 在 `.bashrc` 或 `.profile` 中添加
     ```bash
     export DB_USER=postgres
     export DB_PASSWORD=your_password
     export DB_HOST=localhost
     export DB_PORT=5432
     export DB_NAME=damaihelper
     ```
   - macOS: 在 `.bash_profile` 或 `.zshrc` 中添加
     ```bash
     export DB_USER=postgres
     export DB_PASSWORD=your_password
     export DB_HOST=localhost
     export DB_PORT=5432
     export DB_NAME=damaihelper
     ```

### 云服务器环境

1. **使用DATABASE_URL**
   对于云环境（如Heroku、AWS RDS、Azure PostgreSQL等），只需设置 `DATABASE_URL` 环境变量：
   
   ```env
   DATABASE_URL=postgresql://username:password@host:port/database
   ```
   
   系统会自动优先使用这个URL进行数据库连接，优先级高于单独设置的DB_*环境变量。
   
   **注意**：在云环境中，您可以将 `DATABASE_URL` 设置为环境变量，也可以在 `.env` 文件中定义它。

2. **主流云服务配置示例**
   - **Heroku**: 部署时自动配置 `DATABASE_URL` 环境变量
   - **AWS RDS**: 获取终端节点和凭证，构建连接URL
   - **Azure Database for PostgreSQL**: 使用提供的连接字符串

## 数据库模型结构

项目使用SQLModel定义了以下核心模型：

1. **UserAccount**: 用户/账户信息
   - 存储大麦账号凭证和配置
   - 关联到多个抢票任务

2. **TicketTask**: 抢票任务信息
   - 任务ID、状态、进度
   - 关联的账户、场次、票档信息
   - 任务结果和时间记录

3. **ProxyIP**: 代理IP池管理
   - IP地址、端口、协议
   - 可用性状态和响应时间

4. **TaskLog**: 任务执行日志
   - 详细记录每个任务的执行过程
   - 支持不同日志级别和详细信息

## 安装依赖

项目需要以下数据库相关依赖：

```bash
# 安装数据库依赖
pip install -r requirements_db.txt
```

`requirements_db.txt` 包含：
- SQLModel: 结合SQLAlchemy和Pydantic的ORM框架
- psycopg2-binary: PostgreSQL数据库驱动
- 其他必要的依赖包

## 启动服务

### Windows

```bash
# 使用提供的FastAPI启动脚本
fastapi_win_start.bat
```

### Ubuntu

```bash
# 授予执行权限
chmod +x fastapi_ubuntu_start.sh

# 运行启动脚本
./fastapi_ubuntu_start.sh
```

服务启动时会自动初始化数据库表结构（如果不存在）。

## 数据库迁移

当需要修改数据库模型时，建议使用Alembic进行数据库迁移管理。

## 数据安全注意事项

1. **密码加密**: 生产环境中应使用加密方式存储用户密码
2. **环境变量**: 敏感信息（如数据库凭证）应通过环境变量提供，不要硬编码在代码中
3. **访问控制**: 配置PostgreSQL的访问控制列表，限制外部访问
4. **连接池**: 生产环境中配置适当的数据库连接池大小

## 常见问题排查

### 连接失败
- 检查PostgreSQL服务是否正在运行
- 验证数据库凭证是否正确
- 确认防火墙设置允许连接
- 检查环境变量配置是否正确

### 表创建失败
- 确保数据库用户有创建表的权限
- 检查数据库连接URL格式是否正确
- 查看服务日志获取详细错误信息

### 性能问题
- 为常用查询字段添加索引
- 调整数据库连接池配置
- 考虑使用异步数据库操作

## 未来扩展方向

1. **数据备份策略**: 实现定期自动备份
2. **读写分离**: 支持高并发场景
3. **分布式数据库**: 大规模部署时的扩展方案
4. **数据可视化**: 基于历史数据的分析和展示功能

## 与React前端集成

React前端可以通过FastAPI提供的RESTful API与数据库交互：

1. 获取历史任务记录
2. 管理用户账户信息
3. 配置和优化代理池
4. 查看任务执行日志

数据库的引入为项目提供了更强大的数据管理能力，为未来的功能扩展奠定了基础。