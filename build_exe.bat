@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -m pip install pyswisseph tzdata pyinstaller
pyinstaller --noconfirm --onefile --windowed --name LankaJyothisha lanka_jyothisha.py
echo.
echo EXE file: dist\LankaJyothisha.exe
pause
