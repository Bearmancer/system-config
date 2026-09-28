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
    $repoRoot = $PSScriptRoot
    $robocopyFlags = @('/R:1', '/W:1', '/NFL', '/NDL', '/NJH', '/NJS', '/NP')
    $failed = $false

    function Copy-Mirror {
        param([string]$Source, [string]$Dest, [string[]]$ExtraFlags = @())
        if (-not (Test-Path $Source)) { return }
        New-Item -ItemType Directory -Force -Path $Dest | Out-Null
        robocopy $Source $Dest @robocopyFlags @ExtraFlags | Out-Null
        if ($LASTEXITCODE -ge 8) { $script:failed = $true }
    }

    function Copy-Files {
        param([string]$SourceDir, [string[]]$Files, [string]$Dest)
        if (-not (Test-Path $SourceDir)) { return }
        New-Item -ItemType Directory -Force -Path $Dest | Out-Null
        foreach ($f in $Files) {
            $src = Join-Path $SourceDir $f
            if (Test-Path $src) { Copy-Item $src -Destination $Dest -Force }
        }
    }

    # claude/
    Copy-Files -SourceDir "$HOME\.claude" -Files @('CLAUDE.md', 'keybindings.json', 'settings.json') -Dest "$repoRoot\claude"
    Copy-Mirror -Source "$HOME\.claude\skills" -Dest "$repoRoot\claude\skills" -ExtraFlags @('/MIR', '/XJ', '/XD', 'synced', '*-workspace')
    Copy-Mirror -Source "$HOME\.claude\agents" -Dest "$repoRoot\claude\agents" -ExtraFlags @('/MIR')
    Copy-Mirror -Source "$HOME\.claude\commands" -Dest "$repoRoot\claude\commands" -ExtraFlags @('/MIR')

    # opencode/
    Copy-Files -SourceDir "$HOME\.config\opencode" -Files @('AGENTS.md', 'opencode.jsonc', 'tui.json') -Dest "$repoRoot\opencode"
    Copy-Mirror -Source "$HOME\.config\opencode\agents" -Dest "$repoRoot\opencode\agents" -ExtraFlags @('/MIR')
    Copy-Mirror -Source "$HOME\.config\opencode\commands" -Dest "$repoRoot\opencode\commands" -ExtraFlags @('/MIR')
    Copy-Mirror -Source "$HOME\.config\opencode\skills" -Dest "$repoRoot\opencode\skills" -ExtraFlags @('/MIR')

    # omo/
    Copy-Files -SourceDir "$HOME\.omo" -Files @('omo.jsonc') -Dest "$repoRoot\omo"
    Copy-Mirror -Source "$HOME\.omo\scripts" -Dest "$repoRoot\omo\scripts" -ExtraFlags @('/MIR')
    Copy-Mirror -Source "$HOME\.omo\plans" -Dest "$repoRoot\omo\plans" -ExtraFlags @('/MIR')

    # agents/
    Copy-Files -SourceDir "$HOME\.agents" -Files @('.skill-lock.json') -Dest "$repoRoot\agents"
    Copy-Mirror -Source "$HOME\.agents\skills" -Dest "$repoRoot\agents\skills" -ExtraFlags @('/MIR', '/XJ')

    # powershell/
    if ($PROFILE -and (Test-Path $PROFILE)) {
        New-Item -ItemType Directory -Force -Path "$repoRoot\powershell" | Out-Null
        Copy-Item $PROFILE -Destination "$repoRoot\powershell" -Force
        Select-String -Path $PROFILE -Pattern '^\s*\.\s+["'']?([^"''\s]+\.ps1)' -AllMatches |
            ForEach-Object { $_.Matches } | ForEach-Object {
                $dotSourced = $ExecutionContext.InvokeCommand.ExpandString($_.Groups[1].Value)
                if (Test-Path $dotSourced) { Copy-Item $dotSourced -Destination "$repoRoot\powershell" -Force }
            }
    }

    # settings.json must hold no tokens before first commit
    $settingsDest = "$repoRoot\claude\settings.json"
    if (Test-Path $settingsDest) {
        $content = Get-Content $settingsDest -Raw
        if ($content -match '(?i)(api[_-]?key|token|secret|password)\s*["'':]\s*["''][^"'']{8,}') {
            Remove-Item $settingsDest -Force
            Write-Warning 'settings.json appears to hold a credential; left out of this backup.'
        }
    }

    if ($failed) {
        Write-Warning 'One or more robocopy operations failed (exit code >= 8).'
        return $false
    }

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

    if ($failures.Count -gt 0) {
        Read-Host "FAILED: $($failures -join ', '). Press Enter to close"
        return $false
    }
    return $true
}

# --- Scheduled task installers ----------------------------------------------

function Install-DailySyncTask {
    param([string]$RepoRoot = $PSScriptRoot)
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
    $action = New-ScheduledTaskAction -Execute 'pwsh' -Argument "-NoProfile -File `"$RepoRoot\run-sync.ps1`""
    $trigger = New-ScheduledTaskTrigger -Daily -At 9:00am
    Register-ScheduledTask -TaskName 'Daily sync' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
}

function Install-TopgradeTask {
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
    $action = New-ScheduledTaskAction -Execute 'pwsh' -Argument '-NoProfile -Command "topgrade --yes --no-retry; if ($LASTEXITCODE) { Read-Host ''topgrade FAILED''; exit 1 }"'
    $trigger = New-ScheduledTaskTrigger -Daily -At 10:00am
    Register-ScheduledTask -TaskName 'Topgrade' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
}

function Install-SystemConfigTasks {
    param([string]$RepoRoot = $PSScriptRoot)
    Install-DailySyncTask -RepoRoot $RepoRoot
    Install-TopgradeTask
    Write-Host 'Registered: Daily sync (09:00), Topgrade (10:00).'
}

Export-ModuleMember -Function Sync-Lastfm, Sync-Youtube, Backup-AgentConfig, Sync-Foobar2000, Invoke-DailySync, Install-DailySyncTask, Install-TopgradeTask, Install-SystemConfigTasks
