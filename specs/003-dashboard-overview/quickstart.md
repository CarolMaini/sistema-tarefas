# Quickstart: Dashboard de Acompanhamento Pessoal

Execute na raiz do repositório, no PowerShell.

## Testes focados

```powershell
.\.venv\Scripts\python.exe -m pytest src/apps/dashboard/tests/test_dashboard.py src/apps/dashboard/tests/test_back_navigation.py -q
```

## Qualidade e configuração

```powershell
.\.venv\Scripts\ruff.exe check src/apps/dashboard
.\.venv\Scripts\python.exe src/manage.py check
.\.venv\Scripts\python.exe src/manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pytest
```

Resultado esperado: todos os testes aprovados, Ruff sem erros, Django check sem alertas e nenhuma migration nova.
