# Contrato de UI: Recorrência e Atribuição de Ocorrência

Contrato interno da aplicação HTML server-rendered. Não define API pública nem adiciona rotas.

## Criar recorrência

- **Rota atual**: `scheduling:create`, POST para `/workspaces/<workspace_id>/tasks/<task_id>/rules/new/`.
- **Ator**: usuário autenticado autorizado por `Workspace.can_create_tasks()`.
- **Campos existentes**: frequência, datas, dias da semana e data âncora.
- **Campo do responsável**: `default_assignee`, opcional; opções limitadas ao proprietário e membros
  ativos do workspace da tarefa, cada usuário apresentado uma única vez.
- **Resultado válido**: salvar a regra, gerar ocorrências e atribuir o responsável padrão a cada
  ocorrência que pertença à regra e cujo responsável continue elegível.
- **Sem responsável padrão**: gerar ocorrências sem atribuição automática.
- **Validação inválida**: o formulário não aceita um usuário externo/inativo e retorna os erros junto
  dos campos; a regra não é salva.
- **Sucesso**: mensagem de sucesso existente e redirecionamento para a lista de tarefas.

## Atribuir responsável a uma ocorrência

- **Rota atual**: `scheduling:occurrence-assign`, POST para
  `/workspaces/<workspace_id>/occurrences/<occurrence_id>/assign/`.
- **Ator**: usuário autenticado autorizado por `Workspace.can_create_tasks()`.
- **Campo**: `user`, identificador do responsável selecionado no formulário existente do detalhe.
- **Aceitos**: proprietário ou membro ativo do workspace da ocorrência.
- **Rejeitados**: pessoa externa, membership inativa, ocorrência de outro workspace ou ator sem
  autorização. A requisição inválida não persiste uma atribuição; as respostas de acesso seguem o
  comportamento `404` já usado pelas views.
- **Repetição**: responder com mensagem informativa de que a pessoa já está atribuída; não criar outro
  registro nem alterar o estado/histórico da atribuição existente.
- **Sucesso novo**: criar uma atribuição pendente e apresentar mensagem de sucesso.
- **Pós-ação**: redirecionar ao detalhe da mesma ocorrência.

## Consultar e executar

- **Rota atual**: `scheduling:occurrence-detail`, GET para
  `/workspaces/<workspace_id>/occurrences/<occurrence_id>/`.
- **Visibilidade**: somente usuário com acesso ao workspace; fora do workspace retorna `404`.
- **Conteúdo**: mostrar todas as atribuições e estados; quando não houver, mostrar o estado vazio já
  existente. A ação de atribuir só aparece para ator autorizado.
- **Execução**: o POST existente do detalhe identifica a atribuição do usuário autenticado; rejeita
  tentativa de registrar execução para outro usuário. A conclusão continua na rota
  `scheduling:complete-assignment` e só conclui a atribuição do próprio usuário após execução registrada.

## Garantias de integridade

- Toda entrada POST é validada no servidor; a seleção HTML não é uma fronteira de segurança.
- A constraint única existente em `(occurrence, user)` permanece ativa.
- Repetir atribuição ou geração não duplica a relação e não reabre atribuições concluídas/canceladas.