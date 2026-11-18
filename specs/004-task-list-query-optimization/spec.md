# Spec: Otimização da listagem de tarefas

## Objetivo
Reduzir consultas ao banco na tela de tarefas, mantendo o comportamento visível e respeitando a data local configurada no Django.

## Requisitos
- A listagem deve carregar as próximas três ocorrências de cada tarefa em uma consulta de prefetch, sem uma consulta adicional por tarefa.
- Ocorrências anteriores à data local atual não devem aparecer.
- A data de referência deve usar `django.utils.timezone.localdate()`.
- A ordenação das ocorrências deve ser crescente por data.
- O escopo de tarefas deve continuar restrito ao workspace autorizado.
- A interface deve continuar exibindo tarefas sem ocorrências futuras e seus estados.

## Fora de escopo
Paginação da listagem, mudanças visuais, alterações de modelo ou migrations.

## Critérios de aceite
- Teste de regressão comprova uma única consulta para carregar ocorrências, mesmo com várias tarefas.
- Teste comprova limite de três ocorrências futuras por tarefa, incluindo a data local atual.
- CI completo aprovado, incluindo Ruff, Django checks, verificação de migrations e suíte de testes.
