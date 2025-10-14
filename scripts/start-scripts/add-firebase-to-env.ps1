# Firebase Credentials Helper
Write-Host "Firebase Credentials Setup" -ForegroundColor Cyan
Write-Host "======================================"
Write-Host ""

# Check for JSON file
$jsonFile = Get-ChildItem -Filter "urbantz-api-*.json" | Select-Object -First 1

if ($jsonFile) {
    Write-Host "Service account JSON found: $($jsonFile.Name)" -ForegroundColor Green
    
    $json = Get-Content $jsonFile.FullName | ConvertFrom-Json
    $projectId = $json.project_id
    $privateKey = $json.private_key -replace "`n", "\n"
    $clientEmail = $json.client_email
    
    Write-Host ""
    Write-Host "Project ID: $projectId"
    Write-Host "Client Email: $clientEmail"
    Write-Host ""
    
    # Auto-add without confirmation
    if (Test-Path .env) {
        Copy-Item .env .env.backup
        Write-Host "Backup created: .env.backup" -ForegroundColor Green
    }
    
    Add-Content .env ""
    Add-Content .env "# Firebase Configuration"
    Add-Content .env "FIREBASE_PROJECT_ID=$projectId"
    Add-Content .env "FIREBASE_PRIVATE_KEY=`"$privateKey`""
    Add-Content .env "FIREBASE_CLIENT_EMAIL=$clientEmail"
    
    Write-Host ""
    Write-Host "✅ Credentials added to .env!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next step: firebase deploy --only functions" -ForegroundColor Cyan
} else {
    Write-Host "No service account JSON found." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Steps:"
    Write-Host "1. Go to: https://console.firebase.google.com/project/urbantz-api-f6aa5/settings/serviceaccounts/adminsdk"
    Write-Host "2. Click 'Generate new private key'"
    Write-Host "3. Download JSON to this folder"
    Write-Host "4. Run this script again"
}

