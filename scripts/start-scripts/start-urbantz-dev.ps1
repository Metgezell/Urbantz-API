# Urbantz Development Server Startup Script
# This script provides stable server management with live-reload

param(
    [switch]$Kill,
    [switch]$Python,
    [switch]$Node,
    [switch]$Both,
    [switch]$Watch,
    [switch]$Help
)

if ($Help) {
    Write-Host "🚀 Urbantz Development Server Manager" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\start-urbantz-dev.ps1 -Python     # Start Python server only"
    Write-Host "  .\start-urbantz-dev.ps1 -Node       # Start Node.js server only"
    Write-Host "  .\start-urbantz-dev.ps1 -Both       # Start both servers"
    Write-Host "  .\start-urbantz-dev.ps1 -Watch      # Start with live-reload"
    Write-Host "  .\start-urbantz-dev.ps1 -Kill       # Kill all running servers"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\start-urbantz-dev.ps1 -Both -Watch  # Start both with live-reload"
    Write-Host "  .\start-urbantz-dev.ps1 -Kill         # Stop everything"
    exit 0
}

function Kill-Servers {
    Write-Host "🛑 Stopping all servers..." -ForegroundColor Red
    
    # Kill Python servers on port 8080
    $pythonProcesses = Get-NetTCPConnection -State Listen -LocalPort 8080 -ErrorAction SilentlyContinue
    if ($pythonProcesses) {
        $pythonProcesses | ForEach-Object {
            Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
            Write-Host "   Killed Python process on port 8080 (PID: $($_.OwningProcess))" -ForegroundColor Yellow
        }
    }
    
    # Kill Node.js servers on port 3001
    $nodeProcesses = Get-NetTCPConnection -State Listen -LocalPort 3001 -ErrorAction SilentlyContinue
    if ($nodeProcesses) {
        $nodeProcesses | ForEach-Object {
            Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
            Write-Host "   Killed Node.js process on port 3001 (PID: $($_.OwningProcess))" -ForegroundColor Yellow
        }
    }
    
    Start-Sleep -Seconds 2
    Write-Host "✅ All servers stopped" -ForegroundColor Green
}

function Start-PythonServer {
    param([switch]$WithWatch)
    
    Write-Host "🐍 Starting Python server..." -ForegroundColor Blue
    
    if ($WithWatch) {
        Write-Host "   With live-reload enabled" -ForegroundColor Cyan
        Start-Process powershell -ArgumentList "-NoProfile", "-Command", "npx watchfiles 'python start-server-fast.py' --extensions py" -WindowStyle Normal
    } else {
        Start-Process powershell -ArgumentList "-NoProfile", "-Command", "python start-server-fast.py" -WindowStyle Normal
    }
    
    # Wait a moment and check if server started
    Start-Sleep -Seconds 3
    $serverRunning = Get-NetTCPConnection -State Listen -LocalPort 8080 -ErrorAction SilentlyContinue
    if ($serverRunning) {
        Write-Host "✅ Python server running on http://localhost:8080" -ForegroundColor Green
        Write-Host "   Health check: http://localhost:8080/api/health" -ForegroundColor Gray
    } else {
        Write-Host "⚠️ Python server may not have started properly" -ForegroundColor Yellow
    }
}

function Start-NodeServer {
    param([switch]$WithWatch)
    
    Write-Host "🟢 Starting Node.js server..." -ForegroundColor Green
    
    if ($WithWatch) {
        Write-Host "   With live-reload enabled" -ForegroundColor Cyan
        Start-Process powershell -ArgumentList "-NoProfile", "-Command", "npm run server:watch" -WindowStyle Normal
    } else {
        Start-Process powershell -ArgumentList "-NoProfile", "-Command", "npm run server" -WindowStyle Normal
    }
    
    # Wait a moment and check if server started
    Start-Sleep -Seconds 3
    $serverRunning = Get-NetTCPConnection -State Listen -LocalPort 3001 -ErrorAction SilentlyContinue
    if ($serverRunning) {
        Write-Host "✅ Node.js server running on http://localhost:3001" -ForegroundColor Green
        Write-Host "   Health check: http://localhost:3001/api/health" -ForegroundColor Gray
    } else {
        Write-Host "⚠️ Node.js server may not have started properly" -ForegroundColor Yellow
    }
}

function Show-Status {
    Write-Host ""
    Write-Host "📊 Server Status:" -ForegroundColor Cyan
    
    $pythonRunning = Get-NetTCPConnection -State Listen -LocalPort 8080 -ErrorAction SilentlyContinue
    $nodeRunning = Get-NetTCPConnection -State Listen -LocalPort 3001 -ErrorAction SilentlyContinue
    
    if ($pythonRunning) {
        Write-Host "   🐍 Python Server: ✅ Running on port 8080" -ForegroundColor Green
    } else {
        Write-Host "   🐍 Python Server: ❌ Not running" -ForegroundColor Red
    }
    
    if ($nodeRunning) {
        Write-Host "   🟢 Node.js Server: ✅ Running on port 3001" -ForegroundColor Green
    } else {
        Write-Host "   🟢 Node.js Server: ❌ Not running" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "🔗 Quick Links:" -ForegroundColor Yellow
    Write-Host "   Frontend: http://localhost:3001" -ForegroundColor Gray
    Write-Host "   Python API: http://localhost:8080/api/health" -ForegroundColor Gray
    Write-Host "   Node.js API: http://localhost:3001/api/health" -ForegroundColor Gray
}

# Main execution
Write-Host "🚀 Urbantz Development Server Manager" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

if ($Kill) {
    Kill-Servers
    exit 0
}

# Check if dependencies are installed
if ($Watch -or $Both) {
    if (!(Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Host "❌ npm not found. Please install Node.js first." -ForegroundColor Red
        exit 1
    }
    
    # Install dependencies if needed
    if (!(Test-Path "node_modules")) {
        Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
        npm install
    }
}

# Kill existing servers first
Kill-Servers

# Start servers based on parameters
if ($Both) {
    Start-PythonServer -WithWatch:$Watch
    Start-NodeServer -WithWatch:$Watch
} elseif ($Python) {
    Start-PythonServer -WithWatch:$Watch
} elseif ($Node) {
    Start-NodeServer -WithWatch:$Watch
} else {
    # Default: start both servers
    Start-PythonServer -WithWatch:$Watch
    Start-NodeServer -WithWatch:$Watch
}

Show-Status

Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "   - Use Ctrl+C in server windows to stop them" -ForegroundColor Gray
Write-Host "   - Run with -Kill to stop all servers" -ForegroundColor Gray
Write-Host "   - Use -Watch for live-reload on code changes" -ForegroundColor Gray
Write-Host "   - Check server status with: .\start-urbantz-dev.ps1 -Help" -ForegroundColor Gray
