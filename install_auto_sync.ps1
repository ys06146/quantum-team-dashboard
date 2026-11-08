param(
    [string]$PythonExecutable = (Join-Path $env:USERPROFILE 'anaconda3\pythonw.exe')
)
$ErrorActionPreference = 'Stop'
$taskName = 'QuantumTeamDashboard-DriveSync'
$syncScript = Join-Path $PSScriptRoot 'sync_drive.py'
if (-not (Test-Path -LiteralPath $PythonExecutable -PathType Leaf)) { throw 'Python executable not found.' }
if (-not (Test-Path -LiteralPath $syncScript -PathType Leaf)) { throw 'sync_drive.py not found.' }
$account = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$oldTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($oldTask -and $oldTask.Description -notlike 'Quantum Team Drive document sync*') {
    throw 'An unrelated task already uses this name; it was not changed.'
}
$action = New-ScheduledTaskAction -Execute $PythonExecutable -Argument "-X utf8 `"$syncScript`" --publish"
$logon = New-ScheduledTaskTrigger -AtLogOn -User $account
$repeat = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 2)
$principal = New-ScheduledTaskPrincipal -UserId $account -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName $taskName -Description 'Quantum Team Drive document sync: validate mapped plan/guides, then publish to ys06146/quantum-team-dashboard.' -Action $action -Trigger @($logon, $repeat) -Principal $principal -Settings $settings -Force | Select-Object TaskName, State
Start-ScheduledTask -TaskName $taskName
Write-Output 'Installed: login trigger and a 2-minute interval. Runs only as the current signed-in user; no password is stored.'
