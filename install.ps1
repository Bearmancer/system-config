#Requires -Version 7
#Requires -RunAsAdministrator
Import-Module "$PSScriptRoot\SystemConfig.psm1" -Force
Install-SystemConfigTasks -RepoRoot $PSScriptRoot
Write-Host 'One-time manual step: run rclone config and create a remote named gdrive (already done if gdrive: is in rclone listremotes).'
