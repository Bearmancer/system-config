#Requires -Version 7

$ErrorActionPreference = 'Stop'
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
    $profileDir = Split-Path $PROFILE -Parent
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
    exit 1
}

Set-Location $repoRoot
git add -A
git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    exit 0
}
$msg = "Backup agent config $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git commit -m $msg
if ($LASTEXITCODE -ne 0) { exit 1 }
git push
if ($LASTEXITCODE -ne 0) { exit 1 }
