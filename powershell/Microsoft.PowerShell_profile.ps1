Import-Module PSReadLine -ErrorAction SilentlyContinue
Set-PSReadLineOption -MaximumHistoryCount 10000 -HistorySearchCursorMovesToEnd:$true -ShowToolTips:$true
Set-PSReadLineOption -PredictionSource History -PredictionViewStyle ListView -ErrorAction Stop

Remove-Alias ls -ErrorAction SilentlyContinue
Remove-Alias rm -ErrorAction SilentlyContinue

Set-Alias ls eza
Set-Alias oc opencode

function la { eza -la }
function rm { coreutils.exe rm @args }

function Start-ArrStack
{
	$exePaths = @(
		"C:\ProgramData\Sonarr\bin\Sonarr.exe",
		"C:\Program Files\SABnzbd\SABnzbd.exe",
		"C:\ProgramData\Prowlarr\bin\Prowlarr.exe",
		"C:\Users\Lance\AppData\Roaming\Emby-Server\system\EmbyServer.exe",
		"C:\Program Files\qBittorrent\qbittorrent.exe"
	)

	foreach ($exePath in $exePaths)
	{ Start-Process -FilePath $exePath }
}

function Stop-ArrStack
{
	$processNames = @("Sonarr", "SABnzbd", "Prowlarr", "EmbyServer", "embytray", "qbittorrent")
	Get-Process -Name $processNames -ErrorAction SilentlyContinue | Stop-Process -Force
}

Invoke-Expression (&{
		(
			zoxide init powershell | Out-String
		)
	})
