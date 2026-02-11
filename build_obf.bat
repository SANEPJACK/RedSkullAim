@echo off
setlocal

echo [1/3] Strip UTF-8 BOM from RedSkullAim.py (if exists)...
powershell -NoProfile -Command "$p='RedSkullAim.py'; $b=[IO.File]::ReadAllBytes($p); if($b.Length -ge 3 -and $b[0]-eq 0xEF -and $b[1]-eq 0xBB -and $b[2]-eq 0xBF){ [IO.File]::WriteAllBytes($p, $b[3..($b.Length-1)]); Write-Host 'BOM removed' } else { Write-Host 'No BOM found' }"
if errorlevel 1 goto :fail

echo [2/3] Obfuscating with PyArmor...
pyarmor gen -O obf RedSkullAim.py
if errorlevel 1 goto :fail

echo [3/3] Building EXE with PyInstaller...
pyinstaller --clean --noconfirm --onefile --noconsole --name RedSkullAim --icon "img/redaim.ico" --add-data "img\redaim.ico;img" --add-data "img\background.png;img" --add-data "obf\pyarmor_runtime_000000;pyarmor_runtime_000000" --hidden-import ctypes obf\RedSkullAim.py
if errorlevel 1 goto :fail

echo.
echo Build complete: dist\RedSkullAim.exe
goto :eof

:fail
echo.
echo Build failed.
exit /b 1

