# 大麦抢票助手 - Docker部署指南

本指南将帮助您使用Docker部署大麦抢票助手的FastAPI后端服务。根据您的需求，我们将仅部署FastAPI部分，不包含PostgreSQL容器和GUI特性。

## 前提条件

- 已安装 [Docker](https://www.docker.com/get-started)
- 已安装 [Docker Compose](https://docs.docker.com/compose/install/)
- 外部PostgreSQL数据库（或本地安装的PostgreSQL）

## 快速开始

### 1. 配置数据库连接

首先，确保您有可用的PostgreSQL数据库，并在项目根目录的 `.env` 文件中配置连接信息：

```env
# 方式一：使用DATABASE_URL（推荐云环境）
# DATABASE_URL=postgresql://username:password@host:port/database

# 方式二：使用单独的数据库配置（推荐本地开发）
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=damaihelper
```

### 2. 构建和启动Docker容器

使用Docker Compose快速构建和启动服务：

```bash
# 在项目根目录执行
 docker-compose up -d --build
```

这将：
- 构建FastAPI应用的Docker镜像
- 启动一个名为`damaihelper-fastapi`的容器
- 将容器的8000端口映射到主机的8000端口

### 3. 访问服务

服务启动后，可以通过以下地址访问：
- FastAPI文档（Swagger UI）：[http://localhost:8000/docs](http://localhost:8000/docs)
- FastAPI文档（ReDoc）：[http://localhost:8000/redoc](http://localhost:8000/redoc)
- 根路由：[http://localhost:8000/](http://localhost:8000/)

## 详细配置

### Dockerfile详解

`Dockerfile` 包含了构建FastAPI应用Docker镜像的完整流程：
- 使用Python 3.12 slim基础镜像
- 安装必要的系统依赖（包括PostgreSQL客户端库）
- 创建Python虚拟环境并安装项目依赖
- 配置健康检查和启动命令

### docker-compose.yml详解

`docker-compose.yml` 文件定义了FastAPI服务的部署配置：

#### 环境变量配置

您可以在 `docker-compose.yml` 的 `environment` 部分配置环境变量，优先级高于 `.env` 文件：

```yaml
environment:
  DATABASE_URL: postgresql://username:password@host:port/database
  # 或
  DB_USER: postgres
  DB_PASSWORD: your_password
  DB_HOST: host.docker.internal  # 连接到宿主机上的PostgreSQL
  DB_PORT: 5432
  DB_NAME: damaihelper
```

**重要提示**：如果您的PostgreSQL数据库运行在宿主机上，在Windows或macOS上使用 `host.docker.internal` 作为主机名；在Linux上，您可能需要使用 `--add-host=host.docker.internal:host-gateway` 参数或其他配置。

#### 数据卷挂载

配置了以下数据卷挂载：
- 项目根目录：便于开发时实时查看和修改代码
- 日志目录：保存应用日志
- 配置目录：保存应用配置文件

## 常用Docker命令

### 启动服务

```bash
docker-compose up -d
```

### 停止服务

```bash
docker-compose down
```

### 查看容器日志

```bash
docker logs damaihelper-fastapi
```

### 进入容器

```bash
docker exec -it damaihelper-fastapi /bin/bash
```

### 重新构建镜像

```bash
docker-compose build
```

### 查看容器状态

```bash
docker ps -a
```

## 生产环境建议

在生产环境中部署时，建议：

1. 使用环境变量而不是 `.env` 文件来配置敏感信息
2. 移除开发模式下的代码挂载卷
3. 配置适当的资源限制（CPU、内存）
4. 考虑使用HTTPS代理（如Nginx）
5. 配置日志轮转和监控

## 高级配置：集成PostgreSQL容器

虽然您要求不带PostgreSQL容器，但我们在 `docker-compose.yml` 中提供了PostgreSQL容器的配置示例。如果您需要docker-compose也管理PostgreSQL，可以：

1. 取消 `docker-compose.yml` 中 `db` 服务和 `volumes` 部分的注释
2. 修改环境变量配置
3. 重新启动服务

## 故障排查

### 容器无法启动

检查容器日志以获取详细错误信息：
```bash
docker logs damaihelper-fastapi
```

### 数据库连接问题

确保：
1. PostgreSQL服务正在运行
2. 连接参数（主机、端口、用户名、密码、数据库名）正确
3. 数据库用户有足够的权限
4. 防火墙规则允许容器访问数据库

### 端口冲突

如果8000端口已被占用，可以修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "自定义端口:8000"
```

## 更新应用

当您更新代码后，需要重新构建和启动容器：

```bash
docker-compose up -d --build
```