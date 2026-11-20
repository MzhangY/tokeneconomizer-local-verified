param([Parameter(Mandatory=$true)][string]$PythonPath, [switch]$SmokeOnly)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$python = (Resolve-Path -LiteralPath $PythonPath).Path
$label = [guid]::NewGuid().ToString('N').Substring(0,6)
$root = Join-Path ([System.IO.Path]::GetTempPath()) ('av-'+$label)
# Short, fresh temporary paths; never reuse or delete old directories.
if (Test-Path -LiteralPath $root) { throw "Scratch path already exists: $root" }
New-Item -ItemType Directory -Path $root | Out-Null
$env:VALIDATION_SCRATCH_DIR = $root
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$script:failures = 0
$runner = Join-Path $PSScriptRoot 'run_isolated.py'
function Run-Check([string]$label, [string[]]$cmdArgs) {
  & $python $runner --python $python --cwd $repo $label @cmdArgs
  if ($LASTEXITCODE -ne 0) { $script:failures += 1; Write-Warning "$label did not pass. Review validation/logs; failures are not hidden." }
}
Run-Check ('token-'+$label) @('-m','pytest','tests','-p','xdist.plugin','-n','4','--dist','worksteal','-rfEs','--tb=short',"--basetemp=$(Join-Path $root 't')")
if ($script:failures -gt 0) { throw "$script:failures validation command(s) failed." }
