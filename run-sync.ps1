#Requires -Version 7

$failures = [System.Collections.Generic.List[string]]::new()

# 1. Google Drive for desktop
if (-not (Get-Process -Name 'GoogleDriveFS' -ErrorAction SilentlyContinue)) {
    $launcher = Get-ChildItem 'C:\Program Files\Google\Drive File Stream' -Filter 'launch.bat' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($launcher) {
        Start-Process $launcher.FullName
    } else {
        $failures.Add('Google Drive (launcher not found)')
    }
}

# 2. Toolbox sync
toolbox sync lastfm
if (-not $?) { $failures.Add('toolbox sync lastfm') }
toolbox sync youtube
if (-not $?) { $failures.Add('toolbox sync youtube') }

# 3. Agent config backup
& "$PSScriptRoot\backup-agents.ps1"
if ($LASTEXITCODE -ne 0) { $failures.Add('backup-agents.ps1') }

# 4. foobar2000 mirror to Drive
$driveTarget = 'D:\My Drive'
$waited = 0
while (-not (Test-Path $driveTarget) -and $waited -lt 60) {
    Start-Sleep -Seconds 2
    $waited += 2
}
if (-not (Test-Path $driveTarget)) {
    $failures.Add('foobar2000 (Drive not mounted)')
} else {
    robocopy "$env:APPDATA\foobar2000-v2" "$driveTarget\foobar2000-v2" /MIR /R:1 /W:1 /NFL /NDL /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { $failures.Add('foobar2000') }
}

# 5. Report
if ($failures.Count -gt 0) {
    Read-Host "FAILED: $($failures -join ', '). Press Enter to close"
    exit 1
}
