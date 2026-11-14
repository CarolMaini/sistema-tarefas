---
description: "Task list for recurring occurrence assignment"
---

# Tasks: Atribuição em Recorrências

**Input**: Design documents from `/specs/001-atribuicao-recorrencias/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/)

**Tests**: Incluídos porque a especificação exige testes para atribuição válida, rejeição de membro externo e bloqueio de duplicidade, além dos cenários de recorrência e execução.

**Organization**: Tarefas agrupadas por história de usuário; alterações compartilhadas de elegibilidade ficam na fase fundacional.

## Formato

Cada tarefa segue `- [ ] Tnnn [P?] [USn?] descrição com caminho exato`. `[P]` marca apenas trabalho em arquivo distinto, sem dependência de tarefa ainda incompleta. Etiquetas de história aparecem apenas nas fases de histórias.

## Phase 1: Setup

**Purpose**: Preparar estrutura compartilhada do projeto.

O repositório já está inicializado com Django, pytest, pytest-django e Ruff; a estrutura de apps e testes existe. Não há setup adicional necessário para esta feature.

---

## Phase 2: Foundational

**Purpose**: Definir uma única regra de elegibilidade, bloqueando divergências entre formulário, gerador e ação manual.

- [X] T001 Add tests for distinct eligible users and eligibility of owner, active member, inactive member, and external user in `src/apps/workspaces/tests/test_models.py`
- [X] T002 Implement reusable eligible-assignee queryset/list and eligibility check on `Workspace` in `src/apps/workspaces/models.py` so the owner and active memberships are returned once and only those users validate

**Checkpoint**: A regra de elegibilidade compartilhada passa nos testes de workspace; as histórias podem reutilizá-la.

---

## Phase 3: User Story 1 - Definir responsável padrão da recorrência (Priority: P1)

**Goal**: Persistir o responsável padrão e aplicá-lo às ocorrências geradas, sem criar atribuições quando não há padrão.

**Independent Test**: Criar uma recorrência com responsável elegível, gerar ocorrências em mais de uma chamada e confirmar uma atribuição por ocorrência; repetir sem padrão e confirmar nenhuma atribuição automática.

### Tests for User Story 1

- [X] T003 [P] [US1] Add recurrence-creation tests for saving an optional eligible default assignee and rejecting an ineligible choice in `src/apps/scheduling/tests/test_views.py`
- [X] T004 [P] [US1] Add generation tests for default-assignee propagation, no default, later date ranges, repeated generation, inactive default assignee, and preservation of existing assignment status in `src/apps/scheduling/tests/test_services.py`

### Implementation for User Story 1

- [X] T005 [US1] Add `ScheduleRule.default_assignee` as an optional `AUTH_USER_MODEL` foreign key with `null=True`, `blank=True`, and `on_delete=PROTECT` in `src/apps/scheduling/models.py`
- [X] T006 [US1] Create the additive migration for nullable `ScheduleRule.default_assignee` with no backfill in `src/apps/scheduling/migrations/0004_schedulerule_default_assignee.py`
- [X] T007 [P] [US1] Bind the optional `default_assignee` ModelChoiceField to the persisted rule field and limit its queryset using the workspace eligibility helper in `src/apps/scheduling/forms.py`
- [X] T008 [P] [US1] Apply the rule's eligible default assignee idempotently to generated occurrences created or first linked to that rule, preserving existing assignments and other-rule links, in `src/apps/scheduling/services.py`
- [X] T009 [US1] Remove the view's post-generation bulk-assignment loop and rely on the persisted rule and occurrence generator in `src/apps/scheduling/views.py`

**Checkpoint**: A regra salva o padrão, futuras gerações o aplicam uma única vez e nenhuma atribuição existente é substituída.

---

## Phase 4: User Story 2 - Atribuir responsável a uma ocorrência (Priority: P1)

**Goal**: Permitir atribuição manual apenas a pessoas elegíveis e bloquear repetições sem alterar histórico.

**Independent Test**: Atribuir membro ativo com sucesso; submeter pessoa externa/inativa e repetir o mesmo membro; confirmar rejeição sem persistência e uma única atribuição preservada.

### Tests for User Story 2

- [X] T010 [P] [US2] Add POST tests for valid owner/member assignment, external and inactive rejection, duplicate feedback without a second row, and denial for actors without task-management permission in `src/apps/scheduling/tests/test_views.py`
- [X] T011 [P] [US2] Add service tests proving repeated assignment returns the existing row without changing its status and ineligible users are rejected without persistence in `src/apps/scheduling/tests/test_services.py`

### Implementation for User Story 2

- [X] T012 [US2] Implement the shared occurrence-assignment operation using workspace eligibility validation and `TaskAssignment.get_or_create` in `src/apps/scheduling/services.py`
- [X] T013 [US2] Update the existing occurrence-assignment POST action to call the shared operation, retain current authorization and redirects, and show informative duplicate feedback in `src/apps/scheduling/views.py`

**Checkpoint**: A atribuição manual valida o ator e o responsável no servidor, é repetível e mantém a constraint única existente.

---

## Phase 5: User Story 3 - Consultar atribuição e executar ocorrência (Priority: P2)

**Goal**: Garantir que o detalhe apresente responsáveis/estados e que a execução continue individual por responsável.

**Independent Test**: Abrir ocorrência com múltiplas atribuições e sem atribuições; conferir nomes, estados e estado vazio. Registrar execução como responsável e confirmar que somente a própria atribuição pode ser concluída.

### Tests for User Story 3

- [X] T014 [US3] Add occurrence-detail regression coverage for all assignees and statuses, empty state, and execution/completion isolation per assignee in `src/apps/scheduling/tests/test_views.py`

### Implementation for User Story 3

O detalhe, os estados, o estado vazio, o formulário de execução e a conclusão individual já existem em `src/apps/scheduling/views.py` e `src/templates/scheduling/occurrence_detail.html`; não há alteração de implementação prevista. Ajustes nesses arquivos só serão necessários se T014 revelar divergência com o contrato.

**Checkpoint**: A informação já entregue pela UI é protegida por testes de regressão sem reescrita desnecessária do template.

---

## Phase 6: Polish & Cross-Cutting Validation

**Purpose**: Verificar migrations, configuração, testes e lint nos arquivos afetados.

- [X] T015 Run the focused pytest suite from `specs/001-atribuicao-recorrencias/quickstart.md` for `src/apps/scheduling/tests/`, `src/apps/workspaces/tests/test_models.py`, and `src/apps/tasks/tests/test_models.py`
- [X] T016 Run `makemigrations --check --dry-run` and `manage.py check` using the commands documented in `specs/001-atribuicao-recorrencias/quickstart.md`
- [X] T017 [P] Run Ruff on the changed scheduling and workspace modules/tests using the command documented in `specs/001-atribuicao-recorrencias/quickstart.md`

---

## Dependências e ordem de execução

### Dependências entre fases

- **Phase 1 Setup**: sem tarefas; o projeto e a infraestrutura de teste já existem.
- **Phase 2 Foundational**: T001 precede T002; ambas são necessárias antes das histórias.
- **US1**: depende da fundação. T003 e T004 podem ser escritos em paralelo; depois T005, T006, T007/T008 em paralelo e T009.
- **US2**: depende da fundação e da infraestrutura de atribuição de US1. T010 e T011 podem ser escritos em paralelo; depois T012 e T013 em sequência.
- **US3**: T014 depende das rotas e atribuições estabilizadas em US1/US2; a UI existente é validada sem mudança estrutural prevista.
- **Polish**: T015 e T016 depois das histórias; T017 pode executar em paralelo com as verificações de teste/configuração.

### Grafo de dependências

```text
T001 -> T002
         |
         +-> T003 + T004 -> T005 -> T006 -> (T007 + T008) -> T009
                                                       |
                                                       +-> T010 + T011 -> T012 -> T013 -> T014
                                                                                           |
                                                                                           +-> T015 + T016 + T017
```

As duas histórias P1 são sequenciadas porque alteram os mesmos serviços e views; a sequência evita conflito de edição, não indica dependência de valor do usuário entre elas.

## Oportunidades de paralelismo

- **US1**: T003 e T004 atuam em arquivos de teste diferentes. Após T006, T007 e T008 podem ser implementadas em paralelo em `forms.py` e `services.py`.
- **US2**: T010 e T011 atuam em arquivos de teste diferentes. A implementação permanece sequencial: T012 define a operação usada por T013.
- **US3**: T014 é a única tarefa da história; não há paralelismo interno seguro previsto.
- **Polish**: Ruff (T017) pode executar em paralelo com pytest e checks de Django (T015/T016), pois não modifica arquivos.

### Exemplo de execução paralela

```text
US1 tests: T003 in src/apps/scheduling/tests/test_views.py
           T004 in src/apps/scheduling/tests/test_services.py

US2 tests: T010 in src/apps/scheduling/tests/test_views.py
           T011 in src/apps/scheduling/tests/test_services.py
```

## Mapeamento de requisitos

- **FR-001**: T001-T002, T003, T007
- **FR-002**: T003, T005-T007
- **FR-003**: T004-T009
- **FR-004-FR-007**: T010-T013
- **FR-008-FR-009**: T014
- **FR-010**: T001-T002, T010-T013

## Estratégia de implementação

### MVP recomendado

Entregar **US1 e US2 juntas** como incremento mínimo: ambas têm prioridade P1, e US1 isolada não cobre
rejeição de membros inválidos nem integridade da atribuição manual. Executar T001-T013, validar o fluxo
de atribuição default/manual e então integrar US3.

### Entrega incremental

1. Construir elegibilidade compartilhada e sua cobertura (T001-T002).
2. Entregar responsável padrão persistido e propagado às ocorrências (T003-T009).
3. Entregar atribuição manual validada e idempotente (T010-T013).
4. Confirmar detalhe/execução com regressão (T014).
5. Rodar a validação final (T015-T017).

## Notas

- `[P]` significa tarefas independentes em arquivos distintos, sem dependências incompletas.
- Cada tarefa tem identificador sequencial, etiqueta de história nas fases US e caminho de arquivo explícito.
- As constraints de `TaskAssignment` e `TaskOccurrence` são reutilizadas; não criar constraints ou modelos duplicados.
- Esta lista não implementa recursos de notificação, auditoria, edição ou remoção de atribuições.