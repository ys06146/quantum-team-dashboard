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
# Drive creates desktop.ini inside every directory, including .git/refs. Keep
# Git internals on the local disk and retain the original as a reversible backup.
$gitSource = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '.git'))
if ((Get-Item -LiteralPath $gitSource -Force).PSIsContainer) {
    $workspacePath = [IO.Path]::GetFullPath($PSScriptRoot).TrimEnd('\') + '\'
    $cacheRoot = [IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'QuantumTeamDashboard'))
    $gitTarget = [IO.Path]::GetFullPath((Join-Path $cacheRoot 'repo.git'))
    $gitBackup = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '.git-drive-backup'))
    if (-not $gitSource.StartsWith($workspacePath, [StringComparison]::OrdinalIgnoreCase) -or
        -not $gitBackup.StartsWith($workspacePath, [StringComparison]::OrdinalIgnoreCase) -or
        -not $gitTarget.StartsWith($cacheRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Git metadata paths failed the workspace boundary check.'
    }
    if ((Test-Path -LiteralPath $gitTarget) -or (Test-Path -LiteralPath $gitBackup)) {
        throw 'A Git metadata destination already exists; it was not overwritten.'
    }
    New-Item -ItemType Directory -Path $cacheRoot -Force | Out-Null
    Copy-Item -LiteralPath $gitSource -Destination $gitTarget -Recurse -Force
    $copied = Get-ChildItem -LiteralPath $gitSource -Recurse -File -Force | Where-Object Name -ne 'desktop.ini'
    foreach ($item in $copied) {
        $relative = $item.FullName.Substring($gitSource.Length).TrimStart('\')
        $destination = Join-Path $gitTarget $relative
        if ((Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash) {
            throw 'Git metadata copy verification failed; the original is unchanged.'
        }
    }
    Get-ChildItem -LiteralPath $gitTarget -Recurse -Force -Filter desktop.ini | ForEach-Object {
        $noise = [IO.File]::ReadAllText($_.FullName, [Text.Encoding]::Unicode)
        if ($noise.Contains('[.ShellClassInfo]') -and $noise.Contains('GoogleDriveFS.exe')) {
            Remove-Item -LiteralPath $_.FullName -Force
        }
    }
    # These resolved source/destination paths were checked above before this move.
    Move-Item -LiteralPath $gitSource -Destination $gitBackup
    [IO.File]::WriteAllText($gitSource, 'gitdir: ' + $gitTarget.Replace('\','/') + "`n", [Text.UTF8Encoding]::new($false))
    $gitExecutable = Join-Path $env:ProgramFiles 'Git\cmd\git.exe'
    & $gitExecutable -C $PSScriptRoot config core.worktree $PSScriptRoot
    if ($LASTEXITCODE -ne 0) { throw 'Failed to connect the local Git metadata.' }
    # Packaged desktop apps may redirect AppData. Persist Git's physical path so
    # a scheduled process outside that app sees the same repository.
    $physicalGit = (& $gitExecutable -C $PSScriptRoot rev-parse --absolute-git-dir).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Failed to resolve the physical Git directory.' }
    [IO.File]::WriteAllText($gitSource, 'gitdir: ' + $physicalGit + "`n", [Text.UTF8Encoding]::new($false))
    Write-Output 'Git metadata is now local; the original metadata backup remains on Drive.'
}
$action = New-ScheduledTaskAction -Execute $PythonExecutable -Argument "-X utf8 `"$syncScript`" --publish"
$logon = New-ScheduledTaskTrigger -AtLogOn -User $account
$repeat = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 2)
$principal = New-ScheduledTaskPrincipal -UserId $account -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName $taskName -Description 'Quantum Team Drive document sync: validate mapped plan/guides, then publish to ys06146/quantum-team-dashboard.' -Action $action -Trigger @($logon, $repeat) -Principal $principal -Settings $settings -Force | Select-Object TaskName, State
Start-ScheduledTask -TaskName $taskName
Write-Output 'Installed: login trigger and a 2-minute interval. Runs only as the current signed-in user; no password is stored.'
