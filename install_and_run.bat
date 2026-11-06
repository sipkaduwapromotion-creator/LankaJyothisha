@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -m pip install --upgrade pip
py -m pip install pyswisseph tzdata
py lanka_jyothisha.py
pause
