@echo off
setlocal
cd /d "%~dp0"
title LUMINA - Algebra Studio
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 app.py
) else (
  where python >nul 2>&1
  if %errorlevel%==0 (
    python app.py
  ) else (
    echo Python 3 no esta instalado o no esta disponible en PATH.
    echo Descarga Python desde https://www.python.org/downloads/
    echo Activa la opcion Add Python to PATH durante la instalacion.
    pause
    exit /b 1
  )
)
if errorlevel 1 (
  echo.
  echo No fue posible iniciar LUMINA. Consulta README.md.
  pause
)
endlocal
