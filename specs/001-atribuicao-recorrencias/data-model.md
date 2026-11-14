# Data Model: Atribuição em Recorrências

## ScheduleRule (alteração)

Representa a regra que define quando uma tarefa gera ocorrências.

| Campo | Tipo lógico | Obrigatório | Regra |
|---|---|---:|---|
| `default_assignee` | Referência a usuário | Não | Quando definido, identifica a pessoa atribuída às ocorrências desta regra. Deve ser proprietário ou membro ativo do workspace da tarefa no momento de selecionar e atribuir. |

### Relacionamentos

- Cada `ScheduleRule` pertence a uma `Task` existente.
- A tarefa pertence a um `Workspace`, que define proprietário e memberships.
- Uma regra pode referenciar zero ou um usuário como responsável padrão.
- A exclusão do usuário referenciado é protegida para não apagar silenciosamente a preferência.
- Regras anteriores à migration permanecem com `default_assignee` nulo.

## TaskOccurrence (sem alteração estrutural)

Representa a ocorrência datada de uma tarefa. A constraint existente mantém no máximo uma ocorrência
por par `(task, scheduled_date)`. Uma ocorrência pode estar sem regra, ligada à regra atual ou ligada a
outra regra. O gerador não deve transferir uma ocorrência de uma regra para outra.

## TaskAssignment (sem alteração estrutural)

Representa a responsabilidade individual por uma ocorrência.

| Regra | Comportamento |
|---|---|
| Unicidade | Constraint existente impede mais de uma atribuição por `(occurrence, user)`. |
| Criação repetida | `get_or_create` retorna a atribuição existente sem mudar status, data ou conclusão. |
| Estados | Mantém os estados existentes; conclusão continua independente por responsável. |
| Histórico | Atribuições existentes não são removidas quando a membership se torna inativa. |

## Workspace e WorkspaceMembership (sem alteração estrutural)

- `Workspace.owner` torna o proprietário elegível, mesmo sem membership explícita.
- `WorkspaceMembership(user, workspace, is_active=True)` torna o membro elegível naquele workspace.
- Qualquer papel de membro ativo é elegível para receber atribuição; o papel do ator que altera a
  atribuição é validado separadamente por `Workspace.can_create_tasks()`.
- A lista de elegíveis deve ser distinta quando o proprietário também aparece como membro.

## Fluxo e validações

1. O formulário limita a escolha do padrão ao conjunto elegível e salva a referência na regra.
2. A geração cria ou obtém a ocorrência e confirma que ela está vinculada à regra atual.
3. Para padrão definido e ainda elegível, a geração obtém/cria a atribuição dentro da transação.
4. A ação manual valida autorização do ator e elegibilidade do usuário, e então obtém/cria a mesma
   relação de atribuição.
5. Usuário externo ou membership inativa não gera nova atribuição. A ocorrência e atribuições
   existentes permanecem intactas.

## Migração

Adicionar FK anulável `ScheduleRule.default_assignee` para `settings.AUTH_USER_MODEL`, com proteção à
exclusão. A migration não exige backfill, não altera ocorrências e não cria atribuições para regras
existentes.