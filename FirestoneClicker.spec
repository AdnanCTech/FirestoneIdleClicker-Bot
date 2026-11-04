# PyInstaller spec: one-file console exe. Build with `uv run pyinstaller FirestoneClicker.spec`.
from PyInstaller.utils.hooks import collect_submodules

a = Analysis(
    ["firestone_clicker/__main__.py"],
    pathex=["."],
    hiddenimports=collect_submodules("pynput") + ["mss.windows"],
    datas=[],
    excludes=["tkinter", "unittest", "pytest"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name="FirestoneClicker",
    console=True,
    upx=False,
)
