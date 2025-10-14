@echo off
echo 🚀 Starting Urbantz AI Document Scanner - Fast Mode
echo.

REM Kill any existing Python processes
taskkill /f /im python.exe >nul 2>&1

REM Wait a moment
timeout /t 1 /nobreak >nul

REM Start the server
echo ✅ Starting server on port 8080...
start /b python start-server-fast.py

REM Wait for server to start
timeout /t 3 /nobreak >nul

REM Test the server
echo 🧪 Testing server...
python test-api.py

echo.
echo ✅ Server is ready!
echo 📱 Open your browser: http://localhost:8080
echo.
echo Press any key to stop the server...
pause >nul

REM Stop the server
taskkill /f /im python.exe >nul 2>&1
echo 👋 Server stopped.
