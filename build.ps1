# Build FirestoneClicker.exe and the release zip. Run from the repo root in PowerShell.
$ErrorActionPreference = "Stop"
uv sync
uv run pytest -q
if ($LASTEXITCODE -ne 0) { throw "tests failed" }
uv run pyinstaller --noconfirm --clean FirestoneClicker.spec
if ($LASTEXITCODE -ne 0) { throw "pyinstaller failed" }
$version = (uv run python -c "import firestone_clicker; print(firestone_clicker.__version__)").Trim()
$zip = "dist/FirestoneClicker-$version-win64.zip"
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path dist/FirestoneClicker.exe, settings.toml, README.md, LICENSE -DestinationPath $zip
Write-Host "built $zip"
