#Requires -Version 7

$hookJson = [Console]::In.ReadToEnd() | ConvertFrom-Json
$path = $hookJson.tool_input.file_path
if (-not $path) { exit 0 }

$claudeHome = Join-Path $HOME '.claude'
$watchedDirs = @('skills', 'agents', 'commands') | ForEach-Object { Join-Path $claudeHome $_ }
$isWatched = ($watchedDirs | Where-Object { $path -like "$_\*" }).Count -gt 0
$isWatched = $isWatched -or ($path -eq (Join-Path $claudeHome 'CLAUDE.md'))

if ($isWatched) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', "$PSScriptRoot\..\backup-agents.ps1" -WindowStyle Hidden
}
