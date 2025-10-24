@echo off
echo --- Ejecutando Auditoria de Dependencias (safety) ---
safety check

echo.
echo --- Ejecutando Auditoria de Codigo Inseguro (bandit) ---
rem [CORRECCION V17] Especificar explícitamente qué escanear (ajusta 'app' y '.' si es necesario)
bandit -r app . -ll

echo.
echo --- Ejecutando Busqueda de Secretos (truffleHog) ---
rem [DESHABILITADO] Incompatible con dependencias seguras
rem .\venv\Scripts\trufflehog.exe filesystem --directory .
echo TruffleHog deshabilitado temporalmente debido a conflictos de dependencia.

echo.
echo --- Auditoria Completa ---
pause