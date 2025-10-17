from typing import Dict, List, Optional, Set
from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import json
import time
import asyncio
import threading
import sys
import os

# 导入项目的核心模块
sys.path.append('.')
from scripts.selenium_driver import start_selenium_driver
from scripts.multi_account_manager import manage_multiple_accounts
from scripts.scheduler import schedule_tasks
from scripts.captcha_solver import solve_captcha

# 导入数据库模块
from database import init_db, save_task_to_db, update_task_in_db

app = FastAPI(title="大麦抢票助手 API", version="1.0")

# 允许CORS，支持React前端调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# 任务状态管理器
task_status: Dict[str, Dict] = {}

# Pydantic模型
sys.path = sys.path[1:]  # 修复路径导入问题
class TicketTaskRequest(BaseModel):
    accounts: List[Dict]
    ticket_settings: Dict
    proxy: Optional[Dict] = None

class CaptchaSolveRequest(BaseModel):
    image_data: str
    account_id: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    message: str
    result: Optional[Dict] = None

# 辅助函数
def load_config():
    with open('config/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

async def update_task_status(task_id: str, status: str, progress: int, message: str, result: Optional[Dict] = None):
    task_status[task_id] = {
        "status": status,
        "progress": progress,
        "message": message,
        "result": result,
        "timestamp": time.time()
    }
    # 通过WebSocket广播状态更新
    await manager.broadcast({
        "type": "status_update",
        "task_id": task_id,
        "status": status,
        "progress": progress,
        "message": message
    })
    
    # 更新数据库中的任务状态
    try:
        update_task_in_db(task_id, status, progress, message, result)
    except Exception as e:
        print(f"更新任务状态到数据库失败: {str(e)}")

# 核心任务函数
def run_ticket_task(task_id: str, request_data: TicketTaskRequest):
    # 保存任务到数据库
    try:
        save_task_to_db(task_id, request_data.dict(), "started", 0, "开始执行抢票任务")
    except Exception as e:
        print(f"保存任务到数据库失败: {str(e)}")
        # 数据库错误不影响任务执行
    asyncio.run(update_task_status(task_id, "started", 0, "开始执行抢票任务"))
    
    try:
        # 处理代理池
        if request_data.proxy:
            asyncio.run(update_task_status(task_id, "processing", 10, f"使用代理IP池: {request_data.proxy.get('ip')}:{request_data.proxy.get('port')}"))
            # 初始化代理池逻辑
        
        # 调度抢票任务
        retry_interval = request_data.ticket_settings.get('retry_interval', 5)
        auto_buy_time = request_data.ticket_settings.get('auto_buy_time')
        asyncio.run(update_task_status(task_id, "processing", 20, f"设置抢票任务调度，重试间隔: {retry_interval}秒"))
        
        # 启动抢票操作
        results = []
        for account in request_data.accounts:
            account_id = account.get('id', 'unknown')
            asyncio.run(update_task_status(task_id, "processing", 30, f"开始为账户 {account_id} 执行抢票任务"))
            
            # 执行抢票
            try:
                # 这里调用现有的抢票逻辑
                result = manage_multiple_accounts(account, request_data.ticket_settings)
                results.append({"account_id": account_id, "success": True, "data": result})
                asyncio.run(update_task_status(task_id, "processing", 50 + len(results) * 10, f"账户 {account_id} 抢票成功"))
            except Exception as e:
                results.append({"account_id": account_id, "success": False, "error": str(e)})
                asyncio.run(update_task_status(task_id, "processing", 50 + len(results) * 10, f"账户 {account_id} 抢票失败: {str(e)}"))
        
        asyncio.run(update_task_status(task_id, "completed", 100, "所有账户抢票任务完成", {"results": results}))
    except Exception as e:
        asyncio.run(update_task_status(task_id, "failed", 0, f"任务执行出错: {str(e)}"))

# API端点
@app.post("/api/ticket/task", response_model=Dict)
async def create_ticket_task(request: TicketTaskRequest, background_tasks: BackgroundTasks):
    """创建一个新的抢票任务"""
    task_id = f"task_{int(time.time())}"
    task_status[task_id] = {
        "status": "pending",
        "progress": 0,
        "message": "任务已创建，等待执行"
    }
    
    # 保存任务到数据库
    try:
        save_task_to_db(task_id, request.dict(), "pending", 0, "任务已创建，等待执行")
    except Exception as e:
        print(f"保存任务到数据库失败: {str(e)}")
        # 数据库错误不影响任务创建
    
    # 在后台线程中执行抢票任务
    background_tasks.add_task(
        lambda: threading.Thread(target=run_ticket_task, args=(task_id, request)).start()
    )
    
    return {"task_id": task_id, "status": "任务已创建", "url": f"/api/ticket/task/{task_id}"}

@app.get("/api/ticket/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """获取抢票任务的状态"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    status = task_status[task_id]
    return TaskStatusResponse(
        task_id=task_id,
        status=status["status"],
        progress=status.get("progress", 0),
        message=status["message"],
        result=status.get("result")
    )

@app.post("/api/captcha/solve", response_model=Dict)
async def solve_captcha_api(request: CaptchaSolveRequest):
    """解决验证码"""
    try:
        result = solve_captcha(request.image_data)
        return {"success": True, "captcha_text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证码识别失败: {str(e)}")

@app.get("/api/config", response_model=Dict)
async def get_config():
    """获取默认配置"""
    try:
        config = load_config()
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"加载配置失败: {str(e)}")

# WebSocket端点
@app.websocket("/ws/task/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket端点，用于实时获取任务状态更新"""
    if task_id not in task_status:
        await websocket.close(code=1008, reason="任务不存在")
        return
    
    await manager.connect(websocket)
    try:
        # 发送当前状态
        current_status = task_status[task_id]
        await websocket.send_json({
            "type": "status_update",
            "task_id": task_id,
            "status": current_status["status"],
            "progress": current_status.get("progress", 0),
            "message": current_status["message"]
        })
        
        # 保持连接直到客户端断开
        while True:
            # 接收客户端消息（如果需要）
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)
        print(f"WebSocket错误: {str(e)}")

# 根端点
@app.get("/")
async def root():
    return {"message": "大麦抢票助手 API", "version": "1.0"}

# 数据库初始化事件处理
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    try:
        init_db()
        print("数据库初始化成功")
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
        # 数据库初始化失败不阻止应用启动

if __name__ == "__main__":
    import uvicorn
    # 先初始化数据库
    try:
        init_db()
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
    uvicorn.run(app, host="0.0.0.0", port=8000)