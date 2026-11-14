# Quickstart: Validar Atribuição em Recorrências

Execute os comandos na raiz do repositório, no PowerShell. A configuração local usa SQLite; PostgreSQL
deve também ser exercitado na CI para validação de concorrência.

## Pré-requisitos

- Ambiente virtual `.venv` configurado com as dependências do projeto.
- Migrações aplicadas antes de executar os testes que usam o banco de desenvolvimento.

## Validações focadas

Executar os testes de geração, views, atribuições e elegibilidade:

```powershell
.\.venv\Scripts\python.exe -m pytest src/apps/scheduling/tests/test_services.py src/apps/scheduling/tests/test_views.py src/apps/workspaces/tests/test_models.py src/apps/tasks/tests/test_models.py -q
```

Resultado esperado: testes aprovados para responsável padrão persistido e ausente, membro válido,
usuário externo/inativo rejeitado, repetição sem duplicidade, autorização, visibilidade e execução
individual.

Verificar migrations e configuração Django:

```powershell
.\.venv\Scripts\python.exe src/manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe src/manage.py check
```

Resultado esperado: nenhuma migration pendente de geração e nenhuma verificação de configuração com
erro.

Executar Ruff nos módulos e testes tocados:

```powershell
.\.venv\Scripts\ruff.exe check src/apps/scheduling src/apps/workspaces/models.py src/apps/workspaces/tests/test_models.py
```

Resultado esperado: Ruff encerra sem erros.

## Cenários funcionais manuais

1. Criar uma recorrência com proprietário como padrão e outra com membro ativo como padrão; abrir
   ocorrências de datas diferentes e confirmar a atribuição individual no detalhe.
2. Criar recorrência sem padrão; confirmar que as ocorrências exibem estado sem atribuição e ainda
   oferecem atribuição manual ao ator autorizado.
3. Tentar atribuir usuário externo ou membro inativo por POST; confirmar rejeição e nenhuma nova linha
   de atribuição.
4. Enviar duas vezes a atribuição para o mesmo responsável; confirmar mensagem informativa, uma única
   atribuição e estado/histórico inalterado.
5. Desativar a membership de um responsável padrão e gerar outro intervalo; confirmar que as ocorrências
   são geradas sem uma nova atribuição para ele e que atribuições anteriores continuam visíveis.
6. Repetir geração e conferir que uma ocorrência ligada a outra regra não é reassociada nem recebe o
   padrão corrente.