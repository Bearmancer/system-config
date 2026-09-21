# Weekly backup: mirrors whitelisted local agent config into the repo clone and pushes.
# Local files are never modified, moved, or symlinked; the repo receives copies only.
# Whitelist and rationale: see README.md. Excludes (plugins, settings, caches) are absent by design.

param(
    [string]$RepoPath = (Join-Path $env:USERPROFILE '.omo\agents-config'),
    [string]$RemoteUrl = 'https://github.com/Bearmancer/agents-config.git'
)

$ErrorActionPreference = 'Stop'

$Log = Join-Path $env:USERPROFILE '.omo\agents-config-sync.log'
function Write-Log([string]$Message) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
    Add-Content -LiteralPath $Log -Value $line
    Write-Output $line
}

function Invoke-Robocopy([string]$Source, [string]$Destination, [string[]]$Extra) {
    $robocopyArgs = @($Source, $Destination) + $Extra + @('/NFL', '/NDL', '/NJH', '/NJS', '/R:1', '/W:1')
    robocopy @robocopyArgs | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed with exit $LASTEXITCODE for $Source -> $Destination" }
}

if (-not (Test-Path -LiteralPath (Join-Path $RepoPath '.git'))) {
    Write-Log "clone missing; cloning $RemoteUrl -> $RepoPath"
    git clone $RemoteUrl $RepoPath
    if ($LASTEXITCODE -ne 0) { throw 'git clone failed' }
}

$c = Join-Path $env:USERPROFILE '.claude'
$o = Join-Path $env:USERPROFILE '.config\opencode'
$m = Join-Path $env:USERPROFILE '.omo'
$a = Join-Path $env:USERPROFILE '.agents'

# Claude: instruction file + keybindings (files only), user skills (mirror; synced + all eval workspaces excluded, junctions skipped)
Invoke-Robocopy $c                (Join-Path $RepoPath 'claude')                @('CLAUDE.md', 'keybindings.json')
Invoke-Robocopy (Join-Path $c 'skills') (Join-Path $RepoPath 'claude\skills')   @('/MIR', '/XJ', '/XD', 'synced', '*-workspace')

# OpenCode: instruction + tool config (files), agents/commands/skills (mirrors)
Invoke-Robocopy $o                (Join-Path $RepoPath 'opencode')              @('AGENTS.md', 'opencode.jsonc', 'tui.json')
Invoke-Robocopy (Join-Path $o 'agents')   (Join-Path $RepoPath 'opencode\agents')   @('/MIR')
Invoke-Robocopy (Join-Path $o 'commands') (Join-Path $RepoPath 'opencode\commands') @('/MIR')
Invoke-Robocopy (Join-Path $o 'skills')   (Join-Path $RepoPath 'opencode\skills')   @('/MIR')

# omo: config + scripts
Invoke-Robocopy $m                (Join-Path $RepoPath 'omo')                   @('omo.jsonc')
Invoke-Robocopy (Join-Path $m 'scripts')  (Join-Path $RepoPath 'omo\scripts')   @('/MIR')

# omo: authored/decision content with no other backup (cache/ and codegraph/ stay
# excluded on purpose — regenerable via yt-dlp / codegraph init, not source material)
Invoke-Robocopy (Join-Path $m 'ulw-research') (Join-Path $RepoPath 'omo\ulw-research') @('/MIR')
Invoke-Robocopy (Join-Path $m 'teach')        (Join-Path $RepoPath 'omo\teach')        @('/MIR')
Invoke-Robocopy (Join-Path $m 'plans')        (Join-Path $RepoPath 'omo\plans')        @('/MIR')
Invoke-Robocopy (Join-Path $m 'notepads')     (Join-Path $RepoPath 'omo\notepads')     @('/MIR')

# agents: the `npx skills add` (skills.sh) install location — canonical bundles + update lock.
# /XJ skips junction/symlink-linked skills (plugin installs) — those are reinstallable, not backups.
Invoke-Robocopy $a                (Join-Path $RepoPath 'agents')                @('.skill-lock.json')
Invoke-Robocopy (Join-Path $a 'skills')   (Join-Path $RepoPath 'agents\skills') @('/MIR', '/XJ')

Push-Location $RepoPath
try {
    git add -A
    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) {
        $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm'
        git -c user.name='Bearmancer' -c user.email='lordlance@outlook.in' commit -m "Sync agent config $stamp" | Out-Null
        if ($LASTEXITCODE -ne 0) { throw 'git commit failed' }
        git push origin HEAD | Out-Null
        if ($LASTEXITCODE -ne 0) { throw 'git push failed' }
        Write-Log "pushed sync commit $stamp"
    }
    else {
        Write-Log 'no changes'
    }
}
finally {
    Pop-Location
}

# Keep the log small (last 500 lines).
$lines = Get-Content -LiteralPath $Log -ErrorAction SilentlyContinue
if ($lines -and $lines.Count -gt 500) {
    $lines[-500..-1] | Set-Content -LiteralPath $Log
}
