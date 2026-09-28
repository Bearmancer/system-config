#Requires -Version 7
#Requires -RunAsAdministrator

$repoRoot = $PSScriptRoot
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew

# Daily sync: 09:00
$dailySyncAction = New-ScheduledTaskAction -Execute 'pwsh' -Argument "-NoProfile -File `"$repoRoot\run-sync.ps1`""
$dailySyncTrigger = New-ScheduledTaskTrigger -Daily -At 9:00am
Register-ScheduledTask -TaskName 'Daily sync' -Action $dailySyncAction -Trigger $dailySyncTrigger -Principal $principal -Settings $settings -Force

# Topgrade: 10:00
$topgradeAction = New-ScheduledTaskAction -Execute 'pwsh' -Argument '-NoProfile -Command "topgrade --yes --no-retry; if ($LASTEXITCODE) { Read-Host ''topgrade FAILED''; exit 1 }"'
$topgradeTrigger = New-ScheduledTaskTrigger -Daily -At 10:00am
Register-ScheduledTask -TaskName 'Topgrade' -Action $topgradeAction -Trigger $topgradeTrigger -Principal $principal -Settings $settings -Force

Write-Host 'Registered: Daily sync (09:00), Topgrade (10:00).'
Write-Host 'One-time manual step: run rclone config and create a remote named gdrive.'
