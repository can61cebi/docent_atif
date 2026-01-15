@echo off
chcp 65001 >nul
echo.
echo DOÇENTLİK ATIF DOSYASI OLUŞTURMA ARACI
echo KURULUM SCRİPTİ
echo.

echo [1/4] Python kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python bulunamadi! Lutfen python.org'dan yukleyin.
    pause
    exit /b 1
)
echo Python bulundu

echo.
echo [2/4] Virtual environment olusturuluyor...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment olusturuldu
) else (
    echo Virtual environment zaten mevcut
)

echo.
echo [3/4] Bagimliliklar yukleniyor...
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo Bagimliliklar yuklendi

echo.
echo [4/4] Playwright tarayicisi yukleniyor...
playwright install chromium
echo Chromium yuklendi

echo.
echo KURULUM TAMAMLANDI!
echo Programi calistirmak icin: run.bat
echo.
pause
