@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo  VisionControl - Nuitka Build
echo ========================================
echo.

REM Ativa o venv
call venv\Scripts\activate.bat

REM Build com Nuitka
python -m nuitka --standalone ^
    --enable-plugin=tk-inter ^
    --mingw64 ^
    --assume-yes-for-downloads ^
    --output-dir=dist ^
    main.py

REM Copia config.json e DLLs extras
if exist dist\main.dist (
    copy /Y config.json dist\main.dist\ 2>nul
    copy /Y "%WINDIR%\System32\concrt140.dll" dist\main.dist\ 2>nul
    copy /Y "%WINDIR%\System32\msvcp140.dll" dist\main.dist\ 2>nul
    echo.
    echo Build concluido! Executavel em: dist\main.dist\main.exe
) else (
    echo ERRO: Build falhou.
)

pause
