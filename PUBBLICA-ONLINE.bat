@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo.
echo ==================================================
echo   SitoWeb.info - genera blog + pubblica online
echo ==================================================
echo.

where git >nul 2>nul
if errorlevel 1 (
    echo ERRORE: Git non trovato nel PATH.
    pause
    exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
    echo ERRORE: Python non trovato nel PATH.
    pause
    exit /b 1
)

if not exist ".git" (
    echo ERRORE: questa cartella non sembra essere la root del repository Git.
    echo Cartella attuale:
    cd
    pause
    exit /b 1
)

if not exist "scripts\build_blog.py" (
    echo ERRORE: non trovo scripts\build_blog.py
    pause
    exit /b 1
)

echo [1/6] Rigenero articoli, blog, sitemap, robots e RSS...
python scripts\build_blog.py

if errorlevel 1 (
    echo.
    echo ERRORE: build_blog.py non e' riuscito. Push annullato.
    pause
    exit /b 1
)

echo.
echo [2/6] Stato modifiche dopo la generazione:
git status --short

echo.
git status --short > "%TEMP%\sitoweb_git_status.txt"

for %%A in ("%TEMP%\sitoweb_git_status.txt") do (
    if %%~zA==0 (
        echo Nessuna modifica da pubblicare.
        del "%TEMP%\sitoweb_git_status.txt" >nul 2>nul
        echo.
        echo Apro comunque il sito...
        start "" "https://sitoweb.info/blog.html"
        pause
        exit /b 0
    )
)

del "%TEMP%\sitoweb_git_status.txt" >nul 2>nul

echo.
set /p msg=Messaggio commit, lascia vuoto per automatico: 

if "%msg%"=="" (
    for /f "tokens=1-4 delims=/ " %%a in ("%date%") do set oggi=%%a-%%b-%%c
    for /f "tokens=1-2 delims=: " %%a in ("%time%") do set ora=%%a-%%b
    set msg=Aggiornamento articoli blog %oggi% %ora%
)

echo.
echo [3/6] Aggiungo modifiche al commit...
git add -A

if errorlevel 1 (
    echo.
    echo ERRORE: git add non riuscito.
    pause
    exit /b 1
)

echo.
echo [4/6] File pronti per il commit:
git diff --cached --name-status

echo.
echo [5/6] Commit...
git commit -m "%msg%"

if errorlevel 1 (
    echo.
    echo Nessun commit creato oppure errore nel commit.
    echo Provo comunque il push, nel caso esistano commit locali non ancora pubblicati...
)

echo.
echo [6/6] Push su GitHub...
git push origin main

if errorlevel 1 (
    echo.
    echo ERRORE: push non riuscito.
    pause
    exit /b 1
)

echo.
echo ==================================================
echo   Fatto. Cloudflare Pages dovrebbe aggiornare il sito.
echo ==================================================
echo.
echo Apro blog e dashboard Cloudflare...
start "" "https://sitoweb.info/blog.html"

echo.
pause