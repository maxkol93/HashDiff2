@echo off
echo ================================
echo Building HashDiff.exe...
echo ================================

pyinstaller ^
  --onefile ^
  --windowed ^
  --name HashDiff ^
  --icon assets/icon.ico ^
  --hidden-import tkinterdnd2 ^
  --collect-data tkinterdnd2 ^
  --add-data "assets;assets" ^
  src/app.py

echo.
if exist dist\HashDiff.exe (
    echo ================================
    echo SUCCESS: dist\HashDiff.exe
    echo ================================
    for %%A in (dist\HashDiff.exe) do echo Size: %%~zA bytes
) else (
    echo ================================
    echo BUILD FAILED
    echo ================================
)
pause
