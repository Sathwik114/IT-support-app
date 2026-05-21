@echo off
echo Installing Electron App...
cd /d "%~dp0"

echo Installing dependencies...
call npm install

echo.
echo Installation complete!
echo.
echo To run the app:
echo   npm start
echo.
echo To build .exe file:
echo   npm run build-win
echo.
pause
