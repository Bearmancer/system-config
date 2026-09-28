#Requires -Version 7

$failures = [System.Collections.Generic.List[string]]::new()

# 1. Toolbox sync
toolbox sync lastfm
if (-not $?) { $failures.Add('toolbox sync lastfm') }
toolbox sync youtube
if (-not $?) { $failures.Add('toolbox sync youtube') }

# 2. Agent config backup
& "$PSScriptRoot\backup-agents.ps1"
if ($LASTEXITCODE -ne 0) { $failures.Add('backup-agents.ps1') }

# 3. foobar2000 mirror via rclone (remote: gdrive)
rclone sync "$env:APPDATA\foobar2000-v2" gdrive:foobar2000-v2 --fast-list
if ($LASTEXITCODE -ne 0) { $failures.Add('foobar2000 (rclone)') }

# 4. Report
if ($failures.Count -gt 0) {
    Read-Host "FAILED: $($failures -join ', '). Press Enter to close"
    exit 1
}
