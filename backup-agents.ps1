#Requires -Version 7
Import-Module "$PSScriptRoot\SystemConfig.psm1" -Force
if (-not (Backup-AgentConfig)) { exit 1 }
