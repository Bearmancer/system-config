#Requires -Version 7
Import-Module "$PSScriptRoot\..\SystemConfig.psm1" -Force

$tmp = Join-Path ([IO.Path]::GetTempPath()) "instructions-test-$([guid]::NewGuid().ToString('N'))"
$start = '<!-- SHARED:START -->'
$end = '<!-- SHARED:END -->'

function Get-Block([string]$Path) {
    $text = ([IO.File]::ReadAllText($Path)).Replace("`r`n", "`n")
    [regex]::Match($text, "(?s)$([regex]::Escape($start))\n(.*?)\n?$([regex]::Escape($end))").Groups[1].Value
}
function Get-Outside([string]$Path) {
    [regex]::Replace([IO.File]::ReadAllText($Path), "(?s)$([regex]::Escape($start)).*?$([regex]::Escape($end))", '')
}
function Assert([bool]$Condition, [string]$Message) {
    if (-not $Condition) { Write-Error "FAIL: $Message"; exit 1 }
}

try {
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    $source = "$tmp\shared.md"
    $crlf = "$tmp\CLAUDE.md"
    $lf = "$tmp\AGENTS.md"
    $bare = "$tmp\bare.md"
    [IO.File]::WriteAllText($source, "# Shared`n`n- rule with `$HOME and `${x} and \1`n- second`n")
    [IO.File]::WriteAllText($crlf, "top`r`n$start`r`nstale`r`n$end`r`nbottom`r`n")
    [IO.File]::WriteAllText($lf, "$start`n$end`n`n## Local`n- keep`n")
    [IO.File]::WriteAllText($bare, "no markers`n")
    $before = @{ crlf = Get-Outside $crlf; lf = Get-Outside $lf; bare = [IO.File]::ReadAllText($bare) }

    $ok = Build-AgentInstructions -SourcePath $source -TargetPath $crlf, $lf, "$tmp\missing.md" 3>$null
    Assert $ok 'builder returns true when every existing target has markers'
    Assert ((Get-Block $crlf) -ceq (Get-Block $lf)) 'marker content must be identical in both outputs'
    Assert ((Get-Block $crlf) -ceq ([IO.File]::ReadAllText($source).Replace("`r`n", "`n").Trim("`n"))) 'marker content must equal the source verbatim'
    Assert ((Get-Outside $crlf) -ceq $before.crlf) 'content outside markers must be unchanged (CRLF target)'
    Assert ((Get-Outside $lf) -ceq $before.lf) 'content outside markers must be unchanged (LF target)'
    Assert (([IO.File]::ReadAllText($crlf) -replace "`r`n", '').Contains("`n") -eq $false) 'CRLF target must stay CRLF only'
    Assert (-not ([IO.File]::ReadAllText($lf).Contains("`r"))) 'LF target must stay LF only'

    $stamp = (Get-Item $crlf).LastWriteTimeUtc
    Start-Sleep -Milliseconds 50
    $null = Build-AgentInstructions -SourcePath $source -TargetPath $crlf, $lf
    Assert ((Get-Item $crlf).LastWriteTimeUtc -eq $stamp) 'second run must not rewrite an up-to-date target'

    $bad = Build-AgentInstructions -SourcePath $source -TargetPath $bare 3>$null
    Assert ((-not $bad) -and ([IO.File]::ReadAllText($bare) -ceq $before.bare)) 'target without markers must return false and stay untouched'

    $noSource = Build-AgentInstructions -SourcePath "$tmp\absent.md" -TargetPath $crlf
    Assert ($noSource -and ((Get-Block $crlf) -ceq (Get-Block $lf))) 'absent source must be a no-op returning true'

    Write-Output 'PASS: marker content identical in both outputs and equal to source; outside-marker content, EOL style and up-to-date targets untouched; missing markers and missing source handled'
} finally {
    Get-ChildItem $tmp -Recurse -Force -ErrorAction SilentlyContinue | Sort-Object FullName -Descending |
        ForEach-Object { if ($_.PSIsContainer) { [IO.Directory]::Delete($_.FullName) } else { [IO.File]::Delete($_.FullName) } }
    if (Test-Path $tmp) { [IO.Directory]::Delete($tmp) }
}
