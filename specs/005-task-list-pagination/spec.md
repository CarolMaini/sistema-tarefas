# Spec: Paginação da listagem de tarefas

## Objetivo
Evitar carregar todas as tarefas de um workspace em uma única resposta, mantendo a experiência atual e as permissões existentes.

## Requisitos
- Exibir até 10 tarefas por página.
- Preservar a ordenação definida pelo modelo (mais recentes primeiro).
- Manter o prefetch das três próximas ocorrências por tarefa na página atual.
- Exibir navegação anterior/próxima e o número da página quando houver mais de uma página.
- Preservar workspace e demais parâmetros de consulta ao navegar.
- Continuar exibindo o estado vazio quando o workspace não tiver tarefas.
- Não alterar regras de autorização nem modelos.

## Critérios de aceite
- Teste com 12 tarefas comprova 10 itens na primeira página e 2 na segunda.
- A navegação entre páginas mantém o workspace e o contexto correto.
- CI completo aprovado, sem migrations.
