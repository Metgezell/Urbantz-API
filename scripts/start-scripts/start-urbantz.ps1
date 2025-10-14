# Urbantz AI Document Scanner Server Startup Script
# PowerShell version with better error handling

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Urbantz AI Document Scanner Server" -ForegroundColor Cyan  
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting server on port 8000..." -ForegroundColor Green
Write-Host "Open your browser and go to: http://localhost:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Magenta
Write-Host ""

try {
    # Check if Python is available
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please install Python and try again" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    
    # Start the server
    python start-server.py
}
catch {
    Write-Host "❌ Error starting server: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Server stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
