@echo off
echo --- Ejecutando Auditoria de Dependencias (safety) ---
safety check

echo.
echo --- Ejecutando Auditoria de Codigo Inseguro (bandit) ---
rem Bandit funciona con '-x venv'
bandit -r . -ll -x venv

echo.
echo --- Ejecutando Busqueda de Secretos (truffleHog) ---
rem [CORRECCION V7] Usar 'filesystem' con el argumento '--directory .'
trufflehog filesystem --directory .

echo.
echo --- Auditoria Completa ---
pause