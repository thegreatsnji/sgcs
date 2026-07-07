@echo off
REM SGCS — Setup local de desenvolvimento (Windows)

echo === SGCS Setup ===

if not exist .env (
    copy .env.example .env
    echo Ficheiro .env criado a partir de .env.example
)

echo.
echo [1/4] A criar ambiente virtual Python...
python -m venv backend\.venv
call backend\.venv\Scripts\activate.bat
pip install -r backend\requirements\development.txt

echo.
echo [2/4] A instalar dependencias do frontend...
cd frontend
call npm install
cd ..

echo.
echo [3/4] A aplicar migracoes...
cd backend
python manage.py migrate
cd ..

echo.
echo [4/4] A criar superutilizador...
python scripts/create_superuser.py

echo.
echo === Setup concluido ===
echo Execute: docker compose up -d db
echo Depois: backend\.venv\Scripts\activate ^&^& cd backend ^&^& python manage.py runserver
echo E: cd frontend ^&^& npm run dev
