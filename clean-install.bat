@echo off
echo Cleaning previous installation...
rmdir /s /q node_modules
del package-lock.json

echo Installing Electron dependencies...
npm install

echo Installation complete!
echo.
echo You can now run the app with: npm run electron
pause
