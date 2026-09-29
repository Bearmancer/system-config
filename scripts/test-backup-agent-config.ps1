#Requires -Version 7
Import-Module "$PSScriptRoot\..\SystemConfig.psm1" -Force

$tmp = Join-Path ([IO.Path]::GetTempPath()) "backup-test-$([guid]::NewGuid().ToString('N'))"
$fakeHome = "$tmp\home"
$fakeRepo = "$tmp\repo"

$sources = @(
    '.claude\CLAUDE.md', '.claude\settings.json', '.claude\keybindings.json',
    '.claude\skills\a\SKILL.md', '.claude\skills\synced\x.md', '.claude\agents\a.md', '.claude\commands\c.md',
    '.config\opencode\opencode.json', '.config\opencode\tui.json', '.config\opencode\AGENTS.md',
    '.config\opencode\agents\a.md', '.config\opencode\commands\c.md',
    '.config\opencode\secrets\key.txt', '.config\opencode\auth.json', '.config\opencode\service.json',
    '.config\opencode\skills\s.md',
    '.omo\agent\settings.json', '.omo\agent\auth.json', '.omo\omo.jsonc', '.omo\scripts\s.ps1', '.omo\plans\p.md',
    '.agents\.skill-lock.json', '.agents\skills\s.md'
)
$expected = @(
    'agents/.skill-lock.json',
    'claude/CLAUDE.md', 'claude/agents/a.md', 'claude/commands/c.md', 'claude/keybindings.json',
    'claude/settings.json', 'claude/skills/a/SKILL.md',
    'omo/settings.json',
    'opencode/AGENTS.md', 'opencode/agents/a.md', 'opencode/commands/c.md', 'opencode/opencode.json', 'opencode/tui.json'
) | Sort-Object

try {
    foreach ($s in $sources) {
        $p = Join-Path $fakeHome $s
        New-Item -ItemType Directory -Force -Path (Split-Path $p) | Out-Null
        Set-Content -Path $p -Value '{}'
    }
    New-Item -ItemType Directory -Force -Path $fakeRepo | Out-Null

    $ok = Backup-AgentConfig -HomeRoot $fakeHome -RepoRoot $fakeRepo -ProfilePath '' -SkipGit
    $actual = Get-ChildItem $fakeRepo -Recurse -File -Force |
        ForEach-Object { $_.FullName.Substring($fakeRepo.Length + 1).Replace('\', '/') } | Sort-Object

    $diff = Compare-Object $expected $actual
    if (-not $ok -or $diff) {
        Write-Error "FAIL: ok=$ok`n$($diff | Out-String)"
        exit 1
    }
    Write-Output "PASS: $($actual.Count) mirrored paths match whitelist"
} finally {
    Get-ChildItem $tmp -Recurse -Force -ErrorAction SilentlyContinue | Sort-Object FullName -Descending |
        ForEach-Object { if ($_.PSIsContainer) { [IO.Directory]::Delete($_.FullName) } else { [IO.File]::Delete($_.FullName) } }
    if (Test-Path $tmp) { [IO.Directory]::Delete($tmp) }
}
