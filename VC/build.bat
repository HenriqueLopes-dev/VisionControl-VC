@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo  VisionControl - Nuitka Build
echo  (Compila Python para C++ otimizado)
echo ========================================
echo.

REM === Valida e ativa o ambiente virtual ===
if not exist "..\.venv\Scripts\activate.bat" (
    echo ERRO: Ambiente virtual nao encontrado em ..\.venv\
    echo Execute primeiro: python -m venv ..\.venv
    pause
    exit /b 1
)
call ..\.venv\Scripts\activate.bat

echo Python: %PYTHON_VERSION%
echo.

REM === Instala Nuitka se necessario ===
pip show nuitka >nul 2>&1
if errorlevel 1 (
    echo [1/3] Instalando Nuitka...
    pip install nuitka
    if errorlevel 1 (
        echo ERRO: Falha ao instalar Nuitka.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Nuitka ja instalado.
)

REM === Build com Nuitka ===
echo [2/3] Compilando Python para C++ (otimizado)...
echo.

python -m nuitka --standalone ^
    --enable-plugin=tk-inter ^
    --mingw64 ^
    --assume-yes-for-downloads ^
    --lto=yes ^
    --jobs=%NUMBER_OF_PROCESSORS% ^
    --include-data-file=config.json=config.json ^
    --include-data-dir=..\.venv\Lib\site-packages\mediapipe\modules=mediapipe/modules ^
    --output-filename=VisionControl.exe ^
    --output-dir=dist ^
    main.py

if errorlevel 1 (
    echo.
    echo [ERRO] Build falhou.
    pause
    exit /b 1
)

echo.
echo [3/3] Build concluido com sucesso!
echo.
echo ========================================
echo  Executavel: dist\main.dist\VisionControl.exe
echo  Pasta completa: dist\main.dist\
echo.
echo  Para distribuir, copie a pasta inteira.
echo  Nao e necessario ter Python instalado
echo  no computador de destino.
echo ========================================
echo.

pause
