# Quickstart: Escopo da conclusão de atribuições

## Cenário de regressão
1. Criar duas ocorrências para a mesma tarefa e workspace.
2. Criar uma atribuição pendente na primeira ocorrência e registrar uma execução.
3. Enviar a requisição de conclusão usando a segunda ocorrência na URL.
4. Esperar HTTP 404 e confirmar que a atribuição continua pendente.

## Validação
A validação automatizada é executada pelo workflow CI do GitHub Actions.