@echo off
REM Orquestração Sprint 18 — validação, logs, materialização (sem inventar preços)
setlocal
cd /d %~dp0..
set DB_HOST=localhost
set LOGDIR=..\docs\logs
if not exist %LOGDIR% mkdir %LOGDIR%

echo === Validacao precos ===
.venv\Scripts\python manage.py validate_precos_validacao_clinica > %LOGDIR%\sprint18_validate_stdout.txt 2>&1

echo === Backup ===
.venv\Scripts\python manage.py sprint18_backup_db > %LOGDIR%\sprint18_backup_stdout.txt 2>&1
if errorlevel 1 (
  echo BACKUP FALHOU - ver log
  exit /b 1
)

echo === Dry-run precos ===
.venv\Scripts\python manage.py import_catalogo_sauvida --file data/precos_validacao_clinica.csv --dry-run --update-existing --actor-email admin@sauvida.gw > %LOGDIR%\sprint18_catalogo_dry_run.txt 2>&1

echo === Materializacao catalogo (sem preco) ===
.venv\Scripts\python manage.py import_catalogo_sauvida --file data/catalogo_servicos_sauvida.csv --apply --materialize-without-price --create-missing-relations --update-existing --actor-email admin@sauvida.gw > %LOGDIR%\sprint18_materialize_apply.txt 2>&1

echo === Dry-run precos apos materializacao ===
.venv\Scripts\python manage.py import_catalogo_sauvida --file data/precos_validacao_clinica.csv --dry-run --update-existing --actor-email admin@sauvida.gw >> %LOGDIR%\sprint18_catalogo_dry_run.txt 2>&1

echo === Import precos apply SKIPPED se zero validas ===
REM Apply de preços só quando precos_validacao_clinica tiver linhas VÁLIDAS

echo === Lab align dry-run ===
.venv\Scripts\python manage.py align_lab_services --dry-run > %LOGDIR%\sprint18_lab_alignment_dry_run.txt 2>&1

echo === Lab align apply ===
.venv\Scripts\python manage.py align_lab_services --apply > %LOGDIR%\sprint18_lab_alignment_apply.txt 2>&1

echo === Relatorios audit ===
.venv\Scripts\python manage.py sprint18_audit_reports

echo Concluido.
endlocal
