@echo off
cd /d "%~dp0"

echo.
echo === SitoWeb.info - aggiorna locale ===
echo.

python scripts\build_blog.py

echo.
echo === Stato modifiche ===
git status --short

echo.
echo Controlla il sito in locale/apri blog.html prima di pubblicare.
pause
