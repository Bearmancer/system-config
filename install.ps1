#Requires -Version 7
#Requires -RunAsAdministrator
Import-Module "$PSScriptRoot\SystemConfig.psm1" -Force
Install-SystemConfigTasks -RepoRoot $PSScriptRoot
# Opens a browser once for Google sign-in.
if (-not (rclone listremotes | Select-String -Quiet '^gdrive:')) { rclone config create gdrive drive scope=drive }
