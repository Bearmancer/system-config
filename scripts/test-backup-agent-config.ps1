#Requires -Version 7
Import-Module "$PSScriptRoot\..\SystemConfig.psm1" -Force

$tmp = Join-Path ([IO.Path]::GetTempPath()) "backup-test-$([guid]::NewGuid().ToString('N'))"
$fakeHome = "$tmp\home"
$fakeRepo = "$tmp\repo"

$sources = @(
    '.claude\CLAUDE.md', '.claude\settings.json',
    '.claude\skills\a\SKILL.md', '.claude\skills\a\__pycache__\m.pyc', '.claude\skills\a\.pytest_cache\c',
    '.claude\skills\synced\x.md', '.claude\agents\a.md', '.claude\commands\c.md',
    '.config\opencode\opencode.json', '.config\opencode\tui.json', '.config\opencode\AGENTS.md',
    '.config\opencode\agents\a.md',
    '.config\opencode\secrets\key.txt', '.config\opencode\auth.json', '.config\opencode\service.json',
    '.config\opencode\skills\s.md',
    '.omo\agent\settings.json', '.omo\agent\auth.json', '.omo\omo.jsonc', '.omo\scripts\s.ps1', '.omo\plans\p.md',
    '.agents\.skill-lock.json', '.agents\skills\s.md'
)
$expected = @(
    'agents/.skill-lock.json',
    'claude/CLAUDE.md', 'claude/agents/a.md', 'claude/commands/c.md',
    'claude/settings.json', 'claude/skills/a/SKILL.md',
    'omo/settings.json',
    'opencode/AGENTS.md', 'opencode/agents/a.md', 'opencode/opencode.json', 'opencode/tui.json'
) | Sort-Object

try {
    foreach ($s in $sources) {
        $p = Join-Path $fakeHome $s
        New-Item -ItemType Directory -Force -Path (Split-Path $p) | Out-Null
        Set-Content -Path $p -Value '{}'
    }
    foreach ($stale in 'claude\keybindings.json', 'opencode\commands\c.md') {
        $p = Join-Path $fakeRepo $stale
        New-Item -ItemType Directory -Force -Path (Split-Path $p) | Out-Null
        Set-Content -Path $p -Value 'stale'
    }

    $noClaude = Backup-AgentConfig -HomeRoot "$tmp\empty" -RepoRoot $fakeRepo -ProfilePath '' -SkipGit 3>$null
    if ($noClaude -or -not (Test-Path "$fakeRepo\claude\keybindings.json")) {
        Write-Error 'FAIL: guard must return $false and remove nothing when HomeRoot has no .claude'
        exit 1
    }

    $lock = [IO.File]::Open("$fakeRepo\claude\keybindings.json", 'Open', 'ReadWrite', 'None')
    try { $locked = Backup-AgentConfig -HomeRoot $fakeHome -RepoRoot $fakeRepo -ProfilePath '' -SkipGit 3>$null } finally { $lock.Dispose() }
    if ($locked) {
        Write-Error 'FAIL: locked stale file must make backup return $false'
        exit 1
    }

    $ok = Backup-AgentConfig -HomeRoot $fakeHome -RepoRoot $fakeRepo -ProfilePath '' -SkipGit
    $actual = Get-ChildItem $fakeRepo -Recurse -File -Force |
        ForEach-Object { $_.FullName.Substring($fakeRepo.Length + 1).Replace('\', '/') } | Sort-Object

    $diff = Compare-Object $expected $actual
    $leftovers = 'claude\keybindings.json', 'opencode\commands' | Where-Object { Test-Path (Join-Path $fakeRepo $_) }
    if (-not $ok -or $diff -or $leftovers) {
        Write-Error "FAIL: ok=$ok`n$($diff | Out-String)"
        exit 1
    }
    Write-Output "PASS: $($actual.Count) mirrored paths match whitelist"
} finally {
    Get-ChildItem $tmp -Recurse -Force -ErrorAction SilentlyContinue | Sort-Object FullName -Descending |
        ForEach-Object { if ($_.PSIsContainer) { [IO.Directory]::Delete($_.FullName) } else { [IO.File]::Delete($_.FullName) } }
    if (Test-Path $tmp) { [IO.Directory]::Delete($tmp) }
}
