@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -m pip install pyswisseph tzdata pyinstaller
pyinstaller --noconfirm --onefile --windowed --add-data "nakshatra_attributes_template.csv;." --name LankaJyothisha lanka_jyothisha.py
echo.
echo EXE file: dist\LankaJyothisha.exe
pause
