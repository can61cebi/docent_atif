@echo off
chcp 65001 >nul
echo.
echo DOÇENTLİK ATIF DOSYASI OLUŞTURMA ARACI
echo 2025 Mart Dönemi Yeni Kriterlerine Uygun
echo.

REM Virtual environment'i aktif et
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment bulunamadi!
    echo Once install.bat calistirin.
    pause
    exit /b 1
)

REM Klasorleri olustur
if not exist "downloads" mkdir downloads
if not exist "output" mkdir output

REM Programi calistir
python main.py

pause
