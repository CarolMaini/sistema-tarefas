# Spec: Escopo da conclusão de atribuições

## Objetivo
Garantir que o identificador da ocorrência informado na URL corresponda à ocorrência da atribuição que será concluída.

## Requisitos
- A conclusão deve localizar a atribuição pelo identificador informado.
- A atribuição deve pertencer à ocorrência indicada na URL.
- A ocorrência deve pertencer ao workspace informado.
- A atribuição deve pertencer ao usuário autenticado e permanecer pendente.
- Requisições com ocorrência divergente devem retornar 404 e não alterar o estado.

## Critérios de aceite
- Teste de regressão comprova que uma atribuição não pode ser concluída por uma URL de outra ocorrência do mesmo workspace.
- Fluxo válido permanece coberto pela suíte existente.
- CI completo aprovado, sem alterações de modelo.