@echo off

echo ===== Setup Starting =====

:: Create destination folder
set DEST=%LOCALAPPDATA%\AutoSyncApp
mkdir "%DEST%" 2>nul

echo.
echo Copying program...
copy "%~dp0test31.exe" "%DEST%" >nul

echo.
echo Starting Resilio Sync (if available)...
if exist "%~dp0Resilio-Sync.exe" (
    start "" "%~dp0Resilio-Sync.exe"
) else (
    echo Resilio Sync not found in pendrive.
)

timeout /t 5

echo.
echo Creating Sync Folder...
mkdir "%USERPROFILE%\ResilioSync\AutoSync" 2>nul

echo.
echo Starting your program...
start "" "%DEST%\test31.exe"

echo.
:: Ask before enabling startup (SAFE)
set /p choice=Do you want to enable auto-start on this PC? (y/n):

if /i "%choice%"=="y" (
    reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v AutoSync /t REG_SZ /d "%DEST%\test3.exe" /f
    echo Auto-start enabled.
) else (
    echo Auto-start skipped.
)

echo.
echo ===== Done =====
pause