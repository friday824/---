Write-Output "=== 日记动漫化 - 开发环境设置 ==="

# Backend setup
Write-Output "`n[1/3] 设置后端..."
Set-Location $PSScriptRoot\..
if (-not (Test-Path .venv)) {
    python -m venv .venv
}
.\.venv\Scripts\python.exe -m pip install fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" alembic aiosqlite dashscope "python-jose[cryptography]" "passlib[bcrypt]" pydantic-settings httpx Pillow python-multipart aiofiles arq redis

# Copy .env if needed
if (-not (Test-Path backend\.env)) {
    Copy-Item backend\.env.example backend\.env
    Write-Output "已创建 backend\.env，请填入你的 DASHSCOPE_API_KEY"
}

# Frontend setup
Write-Output "`n[2/3] 设置前端..."
Set-Location frontend
npm install

# Start Docker for Redis
Write-Output "`n[3/3] 检查 Redis..."
docker compose up -d redis

Write-Output "`n=== 设置完成！==="
Write-Output "启动后端: .\scripts\start_backend.ps1"
Write-Output "启动Worker: .\scripts\start_worker.ps1"
Write-Output "启动前端: .\scripts\start_frontend.ps1"
Write-Output "`n别忘了在 backend\.env 中填入你的阿里云 DashScope API Key！"
