@echo off
cd /d "C:\Users\PC\gabriele\PROGETTI\SITI WEB\sitoweb.info"

echo === Stato modifiche ===
git status --short

echo.
echo === Aggiungo tutto, inclusi html ===
git add -A

echo.
set /p msg=Messaggio commit, lascia vuoto per automatico: 

if "%msg%"=="" (
    set msg=Aggiornamento articoli blog
)

git commit -m "%msg%"

if errorlevel 1 (
    echo.
    echo Nessun commit creato oppure errore.
)

echo.
echo === Push online ===
git push origin main

echo.
echo === Fine ===
pause