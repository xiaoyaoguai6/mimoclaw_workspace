@echo off
echo === AI交易员 启动 ===
echo.

echo [1/2] 启动后端 (FastAPI :8000)...
start "AI-Trader Backend" /min cmd /c "cd /d %~dp0backend && python main.py"
timeout /t 3 /nobreak >nul

echo [2/2] 启动前端 (Vite :3000)...
start "AI-Trader Frontend" /min cmd /c "cd /d %~dp0ai-trader && npm run dev"
timeout /t 5 /nobreak >nul

echo.
echo === 启动完成 ===
echo 后端: http://localhost:8000 (API文档: /docs)
echo 前端: http://localhost:3000
echo.
pause
