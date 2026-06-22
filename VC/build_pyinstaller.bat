@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo  VisionControl - PyInstaller Build
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

REM === Instala dependencias ===
echo [1/3] Instalando dependencias...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias.
    pause
    exit /b 1
)

REM === Garante PyInstaller instalado ===
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller...
    python -m pip install pyinstaller
)

REM === Limpa build anterior ===
if exist "dist_pyinstaller" (
    echo Limpando build anterior...
    rmdir /s /q dist_pyinstaller
)

REM === Build com PyInstaller ===
echo [2/3] Gerando executavel com PyInstaller...
echo.

python -m PyInstaller --onedir ^
    --name VisionControl ^
    --add-data "config.json;." ^
    --collect-all mediapipe ^
    --collect-all cv2 ^
    --hidden-import pynput.keyboard ^
    --hidden-import pynput.mouse ^
    --hidden-import pyautogui ^
    --noconfirm ^
    --clean ^
    --distpath dist_pyinstaller ^
    --workpath build_pyinstaller ^
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
echo  Executavel: dist_pyinstaller\VisionControl\VisionControl.exe
echo.
echo  Para distribuir, copie a pasta inteira:
echo  dist_pyinstaller\VisionControl\
echo.
echo  Nao e necessario ter Python instalado
echo  no computador de destino.
echo ========================================
echo.

pause
