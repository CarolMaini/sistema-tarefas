# Research: Atribuição em Recorrências

## Contexto encontrado

- `ScheduleRule` não persiste responsável padrão. O formulário recebe `assignee`, limitado ao
  proprietário e membros ativos, e a view cria atribuições somente depois da geração inicial.
- `generate_occurrences` já usa `transaction.atomic()` e `get_or_create()` para ocorrências únicas por
  tarefa e data. Uma ocorrência avulsa pode ser vinculada à regra; uma ocorrência de outra regra mantém
  seu vínculo.
- `WorkspaceMembership` registra estado ativo. `Workspace.can_create_tasks()` autoriza atores que
  criam/atribuem tarefas; essa autorização é distinta da elegibilidade da pessoa designada.
- `TaskAssignment` já tem constraint única por ocorrência/usuário. A rota manual atualmente executa
  `exists()` e `create()` separados, embora o detalhe e a confirmação por mensagens já existam.
- A tela de recorrência renderiza todos os campos do formulário; o detalhe da ocorrência já mostra
  responsáveis/estados e permite registrar execução associada ao próprio responsável.

## Decisões

### Persistir a preferência na regra

- **Decision**: Adicionar `ScheduleRule.default_assignee`, FK opcional a `AUTH_USER_MODEL`, anulável e
  com `on_delete=PROTECT`.
- **Rationale**: O responsável é uma preferência da regra, não da tarefa nem de uma chamada isolada. A
  geração futura precisa recuperar a preferência. `PROTECT` segue as relações de criador e atribuição já
  protegidas, evitando perder silenciosamente uma regra que aponta para usuário existente.
- **Alternatives considered**: Manter o campo apenas no formulário (não atende gerações posteriores);
  armazenar o responsável em `Task` (escopo incorreto para tarefas com regras diferentes); `SET_NULL`
  (limpa silenciosamente a configuração se um usuário for excluído).

### Centralizar elegibilidade no workspace

- **Decision**: Expor em `Workspace` a consulta de responsáveis atribuíveis e a validação de usuário
  atribuível. A regra é proprietário ou membro ativo daquele mesmo workspace; a coleção deve ser
  distinta. Formulário, detalhe, serviço e ação manual reutilizam essa definição.
- **Rationale**: Workspace possui proprietário e memberships, portanto é a fronteira de domínio natural.
  A validação no servidor não pode depender apenas das opções HTML.
- **Alternatives considered**: Repetir consultas no formulário, view e gerador (diverge com o tempo);
  usar `can_view()` como elegibilidade (acopla regra de designação à permissão do ator).

### Compartilhar atribuição idempotente

- **Decision**: Criar uma operação do domínio scheduling que valide elegibilidade e use
  `TaskAssignment.get_or_create(occurrence, user)`. A autorização do ator segue na view, usando
  `Workspace.can_create_tasks()`.
- **Rationale**: O serviço será usado tanto pelo gerador quanto pela rota manual. A constraint existente
  fornece integridade sob concorrência; `get_or_create` torna repetições esperadas e não altera status,
  conclusão ou histórico do registro existente.
- **Alternatives considered**: `exists()` seguido de `create()` (corrida entre consulta e gravação);
  retirar a constraint (perde integridade); `update_or_create()` (pode reabrir ou sobrescrever histórico).

### Aplicar o padrão durante geração

- **Decision**: O gerador assegura a atribuição padrão nas ocorrências novas, nas ocorrências avulsas
  associadas à regra atual e nas já vinculadas à mesma regra. Não atribui padrão a ocorrência vinculada
  a regra diferente. Uma atribuição já existente é preservada.
- **Rationale**: A regra deve funcionar em chamadas futuras do gerador e em repetições idempotentes. Se
  uma ocorrência da regra ainda não tiver a atribuição, a geração pode completá-la sem criar duplicata.
  A regra atual não possui fluxo de edição; portanto não há mudança retroativa de padrão pela interface.
- **Alternatives considered**: Atribuir apenas no `CreateView` (repete a limitação atual); atribuir em
  cada ocorrência do mesmo task/date mesmo se ligada a outra regra (atribui política errada); atualizar
  ou substituir atribuições existentes (altera estado/histórico).

### Elegibilidade alterada após criação da regra

- **Decision**: Revalidar o responsável padrão no momento de cada geração. Se ele já não for proprietário
  nem membro ativo, gerar a ocorrência normalmente, sem nova atribuição; manter a preferência e o
  histórico existente.
- **Rationale**: A validade do vínculo é temporal. Falhar toda a geração por uma associação desativada
  interromperia o calendário; atribuir mesmo assim violaria a regra de elegibilidade.
- **Alternatives considered**: Bloquear todas as ocorrências da regra (impacto maior no calendário);
  ignorar desativação (cria atribuições não autorizadas); remover/cancelar atribuições históricas (fora
  do escopo e contrário à spec).

### Interface e contratos

- **Decision**: Reutilizar os formulários HTML e rotas nomeadas existentes; documentar seus campos,
  mensagens e autorização como contrato interno de UI. Não criar endpoint JSON nem rota nova.
- **Rationale**: O projeto é server-rendered e já tem as interações requeridas.
- **Alternatives considered**: Introduzir API ou reescrever os templates (duplicação sem necessidade).

## Stack e verificações

- `pyproject.toml` define Python `>=3.12,<3.13`, Django `6.1.2`, pytest, pytest-django e Ruff.
- A Constitution atual declara o mesmo intervalo Python e versão Django; o gate da stack passa.
- `setup.settings.local` usa SQLite; PostgreSQL permanece o banco primário especificado/configurado para
  o ambiente de produção. Repetição pode ser validada localmente, mas concorrência deve ser coberta no
  banco da CI caso exista execução paralela com PostgreSQL.
- Não há `before_plan` nem `after_plan`: `.specify/extensions.yml` não existe na raiz.