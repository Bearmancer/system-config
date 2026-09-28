#Requires -Version 7
Import-Module "$PSScriptRoot\SystemConfig.psm1" -Force
if (-not (Invoke-DailySync)) { exit 1 }
