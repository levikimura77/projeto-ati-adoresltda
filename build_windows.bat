@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD=python"
py -3 --version >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=py -3"

if not exist ".build-venv\Scripts\python.exe" (
  echo Creating an isolated build environment...
  call %PYTHON_CMD% -m venv .build-venv
  if errorlevel 1 goto :error
)

echo Installing game and build requirements...
call ".build-venv\Scripts\python.exe" -m pip install -r requirements-build.txt
if errorlevel 1 goto :error

echo Building the standalone Windows game...
call ".build-venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean AticadoresLTDA.spec
if errorlevel 1 goto :error

if not exist "release" mkdir "release"
copy /Y "dist\AticadoresLTDA-Campanha.exe" "release\AticadoresLTDA-Campanha.exe" >nul
if errorlevel 1 goto :error
if not exist "site\frontend\downloads" mkdir "site\frontend\downloads"
copy /Y "release\AticadoresLTDA-Campanha.exe" "site\frontend\downloads\AticadoresLTDA-Campanha.exe" >nul
if errorlevel 1 goto :error
copy /Y "LEIA-ME-DISTRIBUICAO.txt" "release\LEIA-ME.txt" >nul
if errorlevel 1 goto :error
powershell -NoProfile -Command "Compress-Archive -Path 'release\AticadoresLTDA-Campanha.exe','release\LEIA-ME.txt' -DestinationPath 'release\AticadoresLTDA-Windows.zip' -Force"
if errorlevel 1 goto :error

echo.
echo Build complete:
echo   release\AticadoresLTDA-Campanha.exe
echo   release\AticadoresLTDA-Windows.zip
echo.
pause
exit /b 0

:error
echo.
echo Build failed. Review the error shown above.
pause
exit /b 1
