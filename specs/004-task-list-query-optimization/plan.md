# Plan: Otimização da listagem de tarefas

1. Adicionar teste de regressão com múltiplas tarefas e ocorrências passadas/futuras.
2. Aplicar `Prefetch` com queryset ordenado, filtrado pela data local e limitado a três ocorrências por tarefa.
3. Remover o loop que dispara consultas individuais no contexto da view.
4. Executar CI e revisar o diff para confirmar ausência de alterações de schema.

## Decisão técnica
Usar `Prefetch(..., to_attr="upcoming_occurrences")` para disponibilizar uma lista já carregada ao template. O queryset limitado preserva o máximo de três ocorrências por tarefa e evita acesso lazy ao related manager.
