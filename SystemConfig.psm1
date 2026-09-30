#Requires -Version 7

# --- Sync services ---------------------------------------------------------

function Sync-Lastfm {
    toolbox sync lastfm
    return $?
}

function Sync-Youtube {
    toolbox sync youtube
    return $?
}

function Backup-AgentConfig {
    param(
        [string]$HomeRoot = $HOME,
        [string]$RepoRoot = $PSScriptRoot,
        [string]$ProfilePath = $PROFILE,
        [switch]$SkipGit
    )
    if (-not $HomeRoot -or -not (Test-Path "$HomeRoot\.claude")) {
        Write-Warning "HomeRoot '$HomeRoot' has no .claude; backup skipped."
        return $false
    }
    $repoRoot = $RepoRoot
    $robocopyFlags = @('/R:1', '/W:1', '/NFL', '/NDL', '/NJH', '/NJS', '/NP')
    $script:failed = $false

    function Copy-Mirror {
        param([string]$Source, [string]$Dest, [string[]]$ExtraFlags = @())
        if (-not (Test-Path $Source)) {
            if (Test-Path $Dest) {
                try { Remove-Item $Dest -Recurse -Force -ErrorAction Stop }
                catch { Write-Warning $_; $script:failed = $true }
            }
            return
        }
        New-Item -ItemType Directory -Force -Path $Dest | Out-Null
        robocopy $Source $Dest @robocopyFlags @ExtraFlags | Out-Null
        if ($LASTEXITCODE -ge 8) { $script:failed = $true }
    }

    function Copy-Files {
        param([string]$SourceDir, [string[]]$Files, [string]$Dest)
        foreach ($f in $Files) {
            $src = Join-Path $SourceDir $f
            if (Test-Path $src) {
                New-Item -ItemType Directory -Force -Path $Dest | Out-Null
                Copy-Item $src -Destination $Dest -Force
            } elseif (Test-Path (Join-Path $Dest $f)) {
                try { Remove-Item (Join-Path $Dest $f) -Force -ErrorAction Stop }
                catch { Write-Warning $_; $script:failed = $true }
            }
        }
    }

    # claude/
    Copy-Files -SourceDir "$HomeRoot\.claude" -Files @('CLAUDE.md', 'keybindings.json', 'settings.json') -Dest "$repoRoot\claude"
    Copy-Mirror -Source "$HomeRoot\.claude\skills" -Dest "$repoRoot\claude\skills" -ExtraFlags @('/MIR', '/XJ', '/XD', 'synced', '*-workspace', '__pycache__', '.pytest_cache')
    Copy-Mirror -Source "$HomeRoot\.claude\agents" -Dest "$repoRoot\claude\agents" -ExtraFlags @('/MIR')
    Copy-Mirror -Source "$HomeRoot\.claude\commands" -Dest "$repoRoot\claude\commands" -ExtraFlags @('/MIR')

    # opencode/
    Copy-Files -SourceDir "$HomeRoot\.config\opencode" -Files @('opencode.jsonc', 'oh-my-opencode-slim.jsonc', 'tui.json', 'AGENTS.md') -Dest "$repoRoot\opencode"
    Copy-Mirror -Source "$HomeRoot\.config\opencode\agents" -Dest "$repoRoot\opencode\agents" -ExtraFlags @('/MIR')
    Copy-Mirror -Source "$HomeRoot\.config\opencode\commands" -Dest "$repoRoot\opencode\commands" -ExtraFlags @('/MIR')

    # omo/
    Copy-Files -SourceDir "$HomeRoot\.omo\agent" -Files @('settings.json', 'mcp.json') -Dest "$repoRoot\omo"

    # agents/
    Copy-Files -SourceDir "$HomeRoot\.agents" -Files @('.skill-lock.json') -Dest "$repoRoot\agents"

    # powershell/
    if ($ProfilePath -and (Test-Path $ProfilePath)) {
        New-Item -ItemType Directory -Force -Path "$repoRoot\powershell" | Out-Null
        Copy-Item $ProfilePath -Destination "$repoRoot\powershell" -Force
        Select-String -Path $ProfilePath -Pattern '^\s*\.\s+["'']?([^"''\s]+\.ps1)' -AllMatches |
            ForEach-Object { $_.Matches } | ForEach-Object {
                $dotSourced = $ExecutionContext.InvokeCommand.ExpandString($_.Groups[1].Value)
                if (Test-Path $dotSourced) { Copy-Item $dotSourced -Destination "$repoRoot\powershell" -Force }
            }
    }

    # mirrored settings files must hold no tokens before first commit; ${VAR} placeholders are allowed
    foreach ($settingsDest in "$repoRoot\claude\settings.json", "$repoRoot\omo\settings.json", "$repoRoot\omo\mcp.json") {
        if (Test-Path $settingsDest) {
            $content = Get-Content $settingsDest -Raw
            if ($content -match '(?i)(api[_-]?key|token|secret|password)["'']?\s*:\s*["''](?!\$\{)[^"'']{8,}') {
                Remove-Item $settingsDest -Force
                Write-Warning "$settingsDest appears to hold a credential; left out of this backup."
            }
        }
    }

    if ($script:failed) {
        Write-Warning 'One or more backup operations failed.'
        return $false
    }

    if ($SkipGit) { return $true }

    Push-Location $repoRoot
    try {
        git add -A
        git diff --cached --quiet
        if ($LASTEXITCODE -eq 0) { return $true }
        $msg = "Backup agent config $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
        git commit -m $msg
        if ($LASTEXITCODE -ne 0) { return $false }
        git push
        return ($LASTEXITCODE -eq 0)
    } finally {
        Pop-Location
    }
}

function Sync-Foobar2000 {
    rclone sync "$env:APPDATA\foobar2000-v2" gdrive:foobar2000-v2 --fast-list
    return ($LASTEXITCODE -eq 0)
}

# --- Orchestrator ------------------------------------------------------------

function Invoke-DailySync {
    $failures = [System.Collections.Generic.List[string]]::new()

    if (-not (Sync-Lastfm)) { $failures.Add('toolbox sync lastfm') }
    if (-not (Sync-Youtube)) { $failures.Add('toolbox sync youtube') }

    try {
        if (-not (Backup-AgentConfig)) { throw 'Backup-AgentConfig returned failure' }
    } catch {
        $failures.Add('backup-agents')
    }

    if (-not (Sync-Foobar2000)) { $failures.Add('foobar2000 (rclone)') }

    try {
        if (-not (Get-Command opencode -ErrorAction SilentlyContinue)) { throw 'opencode not found' }
        $LASTEXITCODE = 0
        opencode service status *> $null
        if ($LASTEXITCODE -ne 0) {
            $LASTEXITCODE = 0
            opencode service start
            if ($LASTEXITCODE -ne 0) { throw 'opencode service start failed' }
            $LASTEXITCODE = 0
            opencode service status *> $null
            if ($LASTEXITCODE -ne 0) { throw 'opencode service still down after start' }
        }
    } catch {
        $failures.Add('opencode service')
    }

    if ($failures.Count -gt 0) {
        Read-Host "FAILED: $($failures -join ', '). Press Enter to close"
        return $false
    }
    return $true
}

# --- Scheduled task installers ----------------------------------------------

function Install-DailySyncTask {
    param([string]$RepoRoot = $PSScriptRoot)
    $pwshPath = (Get-Command pwsh).Source
    $principal = New-ScheduledTaskPrincipal -UserId "$env:COMPUTERNAME\$env:USERNAME" -LogonType Interactive -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
    $action = New-ScheduledTaskAction -Execute $pwshPath -Argument "-NoProfile -File `"$RepoRoot\run-sync.ps1`""
    $trigger = New-ScheduledTaskTrigger -Daily -At 9:00am
    Register-ScheduledTask -TaskName 'Daily sync' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force -ErrorAction Stop | Out-Null
}

function Install-TopgradeTask {
    $pwshPath = (Get-Command pwsh).Source
    $principal = New-ScheduledTaskPrincipal -UserId "$env:COMPUTERNAME\$env:USERNAME" -LogonType Interactive -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
    $action = New-ScheduledTaskAction -Execute $pwshPath -Argument '-NoProfile -Command "topgrade --yes --no-retry; if ($LASTEXITCODE) { Read-Host ''topgrade FAILED''; exit 1 }"'
    $trigger = New-ScheduledTaskTrigger -Daily -At 10:00am
    Register-ScheduledTask -TaskName 'Topgrade' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force -ErrorAction Stop | Out-Null
}

function Install-OpenCodeServiceTask {
    $pwshPath = (Get-Command pwsh).Source
    $user = "$env:COMPUTERNAME\$env:USERNAME"
    $principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
    $action = New-ScheduledTaskAction -Execute $pwshPath -Argument '-NoProfile -Command "opencode service start"'
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $user
    Register-ScheduledTask -TaskName 'OpenCode service' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force -ErrorAction Stop | Out-Null
}

function Install-SystemConfigTasks {
    param([string]$RepoRoot = $PSScriptRoot)
    Install-DailySyncTask -RepoRoot $RepoRoot
    Install-TopgradeTask
    Install-OpenCodeServiceTask
    $expected = 'Daily sync', 'Topgrade', 'OpenCode service'
    $found = @(Get-ScheduledTask -TaskName $expected -ErrorAction SilentlyContinue).Count
    if ($found -ne $expected.Count) {
        throw "Registration reported no error but only $found of $($expected.Count) tasks exist — verify manually."
    }
    Write-Host 'Registered: Daily sync (09:00), Topgrade (10:00), OpenCode service (at logon).'
}

Export-ModuleMember -Function Sync-Lastfm, Sync-Youtube, Backup-AgentConfig, Sync-Foobar2000, Invoke-DailySync, Install-DailySyncTask, Install-TopgradeTask, Install-OpenCodeServiceTask, Install-SystemConfigTasks
