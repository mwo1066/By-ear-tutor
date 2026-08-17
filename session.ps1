# Runs a lesson and keeps the transcript, so a session can be read afterwards
# instead of copied out of the terminal by hand.
#
#   .\session.ps1                 a normal lesson
#   .\session.ps1 --no-intro      skips the opening speech
#   .\session.ps1 --fresh --no-intro
#
# Anything you type after the script name is passed straight to tutor.py.
#
# Three things this does that a bare `python tutor.py` does not:
#
#   -u          unbuffered. WITHOUT IT THE SCREEN STAYS EMPTY until the lesson
#               ends -- measured: three lines a second apart all arrived
#               together at 3.5s once the output was piped.
#   Tee-Object  shows the lesson live AND writes it to logs\.
#   2>          stderr to its own file. PowerShell 5.1 wraps a native command's
#               stderr in six lines of ErrorRecord noise, so it is kept out of
#               the session log rather than allowed to litter it.
#
# Start-Transcript was tried first and does NOT work: it captures PowerShell's
# own streams, not a child process's console output, so the file came back
# without a single line of the lesson in it.

# WITHOUT THIS the Vietnamese is destroyed before it ever reaches the file.
# PowerShell decodes a child process's bytes using [Console]::OutputEncoding,
# which is a legacy codepage on a default Windows install -- Python writes utf-8
# and PowerShell reads it as cp850, so "chị" arrives as "chß╗ï". Seen live on
# 2026-08-17, in both the console and the log.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$stamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$log   = "logs\$stamp.log"
$err   = "logs\$stamp.err.log"

if (-not (Test-Path logs)) { New-Item -ItemType Directory logs | Out-Null }

Write-Host "  session -> $log" -ForegroundColor DarkGray
python -u tutor.py $args 2> $err | Tee-Object -FilePath $log

# Tee-Object writes UTF-16 in PowerShell 5.1 and has NO -Encoding parameter --
# tried, it errors. PowerShell reads its own UTF-16 back fine, but grep and
# Python do not, so the file is rewritten as plain utf-8 once the lesson ends.
(Get-Content $log) | Set-Content $log -Encoding utf8

if ((Get-Item $err).Length -eq 0) { Remove-Item $err }
Write-Host "`n  saved: $log" -ForegroundColor DarkGray
