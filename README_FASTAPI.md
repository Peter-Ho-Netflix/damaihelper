# 大麦抢票助手 - FastAPI 后端实现

本项目将原有的大麦抢票助手转换为一个基于FastAPI的RESTful后端服务，支持通过HTTP API和WebSocket实时状态更新，方便前端React应用调用。

## 功能特点

- ✅ RESTful API 设计，支持创建抢票任务、查询任务状态、解决验证码等功能
- ✅ WebSocket 实时推送任务状态更新
- ✅ 支持多账户同时抢票
- ✅ 支持代理设置
- ✅ 兼容原项目的核心功能

## 安装依赖

首先，安装项目所需的依赖包：

```bash
# 使用pip安装依赖
pip install -r requirements_fastapi.txt

# 或使用conda创建环境（推荐）
conda create --name fastapi_joker python=3.12 -y
conda activate fastapi_joker
pip install -r requirements_fastapi.txt
```

## 启动服务器

### 方式一：直接运行Python文件

```bash
python main_fastapi.py
```

### 方式二：使用uvicorn命令（推荐）

```bash
uvicorn main_fastapi:app --reload --host 0.0.0.0 --port 8000
```

服务器启动后，可通过以下地址访问：
- API文档：http://localhost:8000/docs
- Redoc文档：http://localhost:8000/redoc

## API 端点说明

### 1. 创建抢票任务

```
POST /api/ticket/task
```

**请求体**:
```json
{
  "accounts": [
    {
      "id": "account1",
      "username": "your_username",
      "password": "your_password",
      "platform": "damai" // 或 "taopiaopiao"
    }
  ],
  "ticket_settings": {
    "url": "https://detail.damai.cn/item.htm?id=xxxx",
    "session_id": "session1",
    "ticket_type": "ticket1",
    "quantity": 2,
    "retry_interval": 5,
    "auto_buy_time": "20:00:00"
  },
  "proxy": {
    "ip": "192.168.1.100",
    "port": "8080"
  }
}
```

**响应**:
```json
{
  "task_id": "task_1234567890",
  "status": "任务已创建",
  "url": "/api/ticket/task/task_1234567890"
}
```

### 2. 查询任务状态

```
GET /api/ticket/task/{task_id}
```

**响应**:
```json
{
  "task_id": "task_1234567890",
  "status": "processing",
  "progress": 50,
  "message": "账户 account1 抢票中...",
  "result": null
}
```

### 3. 解决验证码

```
POST /api/captcha/solve
```

**请求体**:
```json
{
  "image_data": "base64_encoded_image_data",
  "account_id": "account1"
}
```

**响应**:
```json
{
  "success": true,
  "captcha_text": "ABCD1234"
}
```

### 4. 获取默认配置

```
GET /api/config
```

**响应**:
```json
{
  "accounts": [...],
  "ticket_settings": {...},
  "proxy_settings": {...}
}
```

## WebSocket 实时状态更新

通过WebSocket连接，可以实时获取任务状态更新：

```
ws://localhost:8000/ws/task/{task_id}
```

**消息格式**:
```json
{
  "type": "status_update",
  "task_id": "task_1234567890",
  "status": "processing",
  "progress": 50,
  "message": "账户 account1 抢票中..."
}
```

## React 前端集成示例

以下是一个简单的React组件示例，展示如何调用FastAPI后端：

```jsx
import React, { useState, useEffect, useRef } from 'react';

function TicketAssistant() {
  const [taskId, setTaskId] = useState('');
  const [taskStatus, setTaskStatus] = useState({ status: 'idle', progress: 0, message: '' });
  const [accounts, setAccounts] = useState([{ username: '', password: '', platform: 'damai' }]);
  const [ticketUrl, setTicketUrl] = useState('');
  const wsRef = useRef(null);

  // 创建抢票任务
  const createTicketTask = async () => {
    const response = await fetch('http://localhost:8000/api/ticket/task', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        accounts: accounts,
        ticket_settings: {
          url: ticketUrl,
          retry_interval: 5
        }
      })
    });
    
    const data = await response.json();
    setTaskId(data.task_id);
    
    // 建立WebSocket连接
    connectWebSocket(data.task_id);
  };

  // 连接WebSocket获取实时更新
  const connectWebSocket = (id) => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    
    wsRef.current = new WebSocket(`ws://localhost:8000/ws/task/${id}`);
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setTaskStatus({
        status: data.status,
        progress: data.progress,
        message: data.message
      });
    };
    
    wsRef.current.onclose = () => {
      console.log('WebSocket连接已关闭');
    };
  };

  // 组件卸载时关闭WebSocket
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return (
    <div className="ticket-assistant">
      <h1>大麦抢票助手</h1>
      
      <div className="task-form">
        <input
          type="text"
          placeholder="输入购票链接"
          value={ticketUrl}
          onChange={(e) => setTicketUrl(e.target.value)}
        />
        <button onClick={createTicketTask}>开始抢票</button>
      </div>
      
      {taskId && (
        <div className="task-status">
          <h2>任务ID: {taskId}</h2>
          <div className="progress-bar">
            <div style={{ width: `${taskStatus.progress}%` }}></div>
          </div>
          <p>进度: {taskStatus.progress}%</p>
          <p>状态: {taskStatus.status}</p>
          <p>消息: {taskStatus.message}</p>
        </div>
      )}
    </div>
  );
}

export default TicketAssistant;
```

## 注意事项

1. 确保ChromeDriver与您的Chrome浏览器版本兼容
2. 生产环境中应修改CORS配置，限制允许的域名
3. 建议使用环境变量存储敏感信息，如账户密码等
4. 对于大规模并发，可能需要调整服务器配置和任务调度策略

## 故障排除

1. **服务器启动失败**: 检查端口8000是否被占用，或尝试使用其他端口
2. **ChromeDriver错误**: 确保chromedriver.exe与您的Chrome版本匹配
3. **CORS错误**: 确认前端域名已添加到后端的CORS白名单中
4. **代理连接问题**: 检查代理服务器设置和网络连接

## License

MIT