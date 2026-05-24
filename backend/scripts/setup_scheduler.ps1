# setup_scheduler.ps1
# Run this script as Administrator to register the Weekly Delivery Task

$ProjectDir = "C:\Users\CBCGaming\Documents\Projects\newsletter-herald"
$PythonExe = "$ProjectDir\backend\venv\Scripts\python.exe"
$ScriptPath = "$ProjectDir\backend\scripts\delivery_worker.py"
$WorkDir = "$ProjectDir\backend"

Write-Host "Registering Newsletter Herald Weekly Sunday Delivery Task..." -ForegroundColor Cyan

# 1. Verify paths exist
if (-not (Test-Path $PythonExe)) {
    Write-Error "Error: Python executable not found at $PythonExe. Please make sure the venv is built."
    Exit 1
}

if (-not (Test-Path $ScriptPath)) {
    Write-Error "Error: Delivery worker script not found at $ScriptPath."
    Exit 1
}

# 2. Define Scheduled Task parameters
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument $ScriptPath -WorkingDirectory $WorkDir
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 8:00AM
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 3. Register Scheduled Task
try {
    Register-ScheduledTask -TaskName "NewsletterHeraldDelivery" -Action $Action -Trigger $Trigger -Settings $Settings -Description "Runs the weekly Sunday 8:00 AM delivery worker for SALLTO Herald bulletins." -Force
    Write-Host "Successfully registered Weekly Task 'NewsletterHeraldDelivery'!" -ForegroundColor Green
    Write-Host "Task will run every Sunday at 8:00 AM." -ForegroundColor Green
} catch {
    Write-Error "Failed to register task. Make sure you are running PowerShell as Administrator: $_"
}
