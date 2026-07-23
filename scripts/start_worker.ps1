Set-Location $PSScriptRoot\..
$env:PYTHONPATH = "$PSScriptRoot\..\backend"
docker compose up -d redis
arq backend.app.worker.run_worker.WorkerSettings --watch backend
