# Place this script into a task scheduler on Windows with "Highest priveleges" and have the task start on startup/login depending how you want this to run. 
# You can also just execute this script at anytime on a machine as long as you are executing out of the directory. 
# This script will automatically identify what is installed and what needs to be removed. The Script has ONE goal and thats to remove anything with Apex One and install Cloud One.

# SCUT tool and Cloud One install script must all exist in the same folder/directory when running this script

# Registry key paths to verify if Apex One is installed and/or Cloud One is installed
$arguments = "-noinstall -dbg"
$cloudOneExists = Test-Path "HKLM:\SOFTWARE\TrendMicro\Deep Security Agent"
$apexExists = Test-Path "HKLM:\SOFTWARE\TrendMicro\Osprey"
$logfilepath = "logs.txt"

Start-Transcript -Path $logfilepath

Write-Host "Checking for elevated permissions..." -ForegroundColor Green
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Insufficient permissions to run this script. Open the PowerShell console as an administrator and run this script again."
    break
}

if ($apexExists -eq $true) {

    Write-Host "Removing Apex One" -ForegroundColor Green

    try {
        $p = Start-Process ".\SCUT.exe" -ArgumentList $arguments -wait -NoNewWindow -PassThru
        $p.HasExited
        $p.ExitCode    
    } catch { 
        Write-Warning "Start-Process encounter error: $_"
        Return # script failed
    }

    if ($p.ExitCode -eq 0) {
        Write-Host "SCUT Succeeded - Forcing Restart" -ForegroundColor Green
        Restart-Computer -Force
    } else {
        Write-Warning "SCUT Failed - Please Check Error logs"
    }
}

# If Cloud One is already installed, it will give a warning and close the script
if ($cloudOneExists -eq $true) {
    Write-Warning "Cloud One Is Already Installed" -ForegroundColor Red
    Start-Sleep -Seconds 3
    Write-Host "Exiting..." -ForegroundColor Red
    Start-Sleep -Seconds 1
}

# If CloudOne doesn't exist, it will begin the install using the script provided in the same directory as this script - no restart is required for Cloud One agents v20+
if ($cloudOneExists -eq $false -and $apexExists -eq $false) {
    Write-Host "Starting Cloud One Agent Install" -ForegroundColor Blue
    Invoke-Expression ".\C1_install.ps1"
}

Stop-Transcript