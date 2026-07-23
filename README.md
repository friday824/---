# 日记动漫化

把你的日记变成温馨的动画短片。AI 自动分析日记内容，生成分镜剧本、绘制场景画面、录制旁白、匹配背景音乐，最终合成一部完整的小动画。

## 技术栈

- **后端**: FastAPI + SQLAlchemy + SQLite
- **前端**: Vue 3 + Vite + Tailwind CSS
- **AI**: 阿里云 DashScope（剧本生成、图片生成、TTS 语音合成）
- **视频合成**: FFmpeg

## 环境要求

- Python >= 3.14
- Node.js >= 18
- FFmpeg（视频合成必需）

## 快速启动

### 1. 克隆项目

```bash
git clone https://github.com/friday824/---.git
cd ---
```

### 2. 启动后端

```powershell
# 创建虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r backend/requirements.txt

# 创建配置文件
copy backend\.env.example backend\.env

# 编辑 backend\.env，填入你的 DashScope API Key
# DASHSCOPE_API_KEY=sk-你的密钥

# 启动后端服务
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

### 4. 访问

打开浏览器访问 `http://localhost:5173`

### 5. 可选：启动 Redis（任务队列）

```bash
docker compose up -d redis
# 然后启动 Worker
.\scripts\start_worker.ps1
```

> 没有 Redis 也可以正常运行，系统会自动降级为后台任务模式。

## 使用流程

1. **注册/登录** — 首次使用需要注册账号
2. **写日记** — 记录今天的点滴
3. **生成视频** — 点击生成按钮，AI 会自动完成：
   - 分析日记内容，生成分镜剧本
   - 绘制每个场景的动画画面
   - 录制温暖的中文旁白
   - 匹配符合情绪的背景音乐
   - 合成最终视频
4. **观看/下载** — 在"我的视频"页面查看和下载生成的动画

## 获取 DashScope API Key

1. 访问 [阿里云 DashScope](https://dashscope.aliyun.com/)
2. 开通模型服务（通义千问、通义万象、CosyVoice）
3. 获取 API Key 填入 `backend\.env`

## 项目结构

```
├── backend/            # FastAPI 后端
│   ├── app/
│   │   ├── api/        # API 路由
│   │   ├── models/     # 数据库模型
│   │   ├── schemas/    # Pydantic 模型
│   │   ├── services/   # 核心服务（剧本/图片/TTS/BGM/合成）
│   │   ├── utils/      # 工具函数
│   │   └── worker/     # 后台任务
│   └── requirements.txt
├── frontend/           # Vue 3 前端
│   ├── src/
│   │   ├── pages/      # 页面组件
│   │   ├── components/ # 通用组件
│   │   └── composables/# 组合式 API
│   └── package.json
├── data/               # 生成数据（视频/图片/音频/BGM）
├── scripts/            # 启动脚本
└── docker-compose.yml  # Redis
```