@echo off
chcp 65001 > nul
echo ===================================
echo  Tour Teresina Golf - Build .exe
echo ===================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado no PATH.
    echo Instale Python 3.10+ e tente novamente.
    pause
    exit /b 1
)

echo [1/3] Instalando dependencias...
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet

echo [2/3] Gerando executavel...
echo (Se aparecer "Acesso negado", feche TourTeresinaGolf.exe e tente de novo.)
python -m PyInstaller --noconfirm TourTeresinaGolf.spec

if errorlevel 1 (
    echo.
    echo ERRO: Build falhou. Veja a mensagem acima.
    pause
    exit /b 1
)

echo [3/3] Concluido!
echo.
echo Executavel gerado em:
echo   dist\TourTeresinaGolf.exe
echo.
echo O arquivo save_data.json e user_settings.json serao criados
echo na mesma pasta do .exe na primeira execucao.
echo.
pause
