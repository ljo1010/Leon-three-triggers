@echo off
chcp 65001 > nul
echo Building LEON: Three Triggers...
echo.

tweego --format=sugarcube-2 -o LEON_Three_Triggers.html src/

if %errorlevel% equ 0 (
    echo.
    echo [OK] Build complete!
    echo Output: LEON_Three_Triggers.html
) else (
    echo.
    echo [FAIL] Build failed.
)

echo.
pause
