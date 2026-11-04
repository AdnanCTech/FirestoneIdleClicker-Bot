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
# Ship the generic defaults, not the owner's personal settings.toml from the repo root.
uv run python -c "from firestone_clicker.paths import DEFAULT_SETTINGS; open('dist/settings.toml', 'w', encoding='utf-8').write(DEFAULT_SETTINGS)"
Compress-Archive -Path dist/FirestoneClicker.exe, dist/settings.toml, README.md, LICENSE -DestinationPath $zip
Write-Host "built $zip"
