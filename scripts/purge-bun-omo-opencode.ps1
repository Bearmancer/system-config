#Requires -Version 7

$ErrorActionPreference = 'Continue'

Get-Process -Name 'OpenCode', 'bun' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

if (Get-Command opencode -ErrorAction SilentlyContinue) {
    opencode uninstall --force
} else {
    foreach ($mgr in 'npm', 'scoop', 'choco') {
        if (Get-Command $mgr -ErrorAction SilentlyContinue) {
            switch ($mgr) {
                'npm'   { npm uninstall -g opencode-ai 2>$null }
                'scoop' { scoop uninstall opencode -g 2>$null }
                'choco' { choco uninstall opencode -y 2>$null }
            }
        }
    }
}

$bunUninstall = Join-Path $HOME '.bun\uninstall.ps1'
if (Test-Path $bunUninstall) {
    & $bunUninstall
} elseif (Get-Command npm -ErrorAction SilentlyContinue) {
    npm uninstall -g bun 2>$null
}

Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*', 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*', 'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -match 'OpenCode' -and $_.UninstallString } |
    ForEach-Object { cmd /c $_.UninstallString }

$leftoverPaths = @(
    "$HOME\.omo"
    "$HOME\.codex"
    "$env:LOCALAPPDATA\Programs\@opencode-aidesktop"
    "$env:LOCALAPPDATA\@opencode-aidesktop-updater"
    "$env:LOCALAPPDATA\OpenCode"
    "$env:LOCALAPPDATA\Programs\OpenCode"
    "$env:APPDATA\OpenCode"
)
foreach ($path in $leftoverPaths) {
    if (Test-Path $path) { Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue }
}

Get-ChildItem "$env:APPDATA\Microsoft\Windows\Start Menu\Programs", "$HOME\Desktop" -Filter '*OpenCode*' -Recurse -ErrorAction SilentlyContinue |
    Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host 'Purge complete. Open a new shell for PATH changes to take effect.'
