# Tarefas: Membros e Navegação do Workspace

**Entrada**: Documentos de design em `/specs/002-workspace-members-navigation/`

**Pré-requisitos**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Organização**: Tarefas agrupadas por história de usuário; testes precedem a implementação correspondente.

## Fase 1: Setup

**Objetivo**: Confirmar a infraestrutura já existente antes das alterações.

- [X] T001 Registrar `apps.audit` em `INSTALLED_APPS` e confirmar Django, pytest, Ruff e padrões de ignore em `src/setup/settings/base.py`, `pyproject.toml`, `.gitignore` e `.dockerignore`

## Fase 2: Fundacional

Não há nova dependência ou estrutura transversal necessária. Os modelos de workspace e associação existentes serão reutilizados; a auditoria será adicionada na história que a exige.

---

## Fase 3: História 1 - Adicionar membro ao workspace (Prioridade: P1)

**Objetivo**: Permitir que proprietária ou gestora associe uma conta ativa existente como colaboradora, sem duplicidade e com registro de auditoria.

**Teste independente**: Criar associação como proprietária/gestora e confirmar lista atualizada e evento de auditoria; rejeitar contas inválidas e não autorizadas sem persistir alterações.

### Testes da História 1

- [X] T002 [P] [US1] Criar testes do evento de auditoria e seus relacionamentos em `src/apps/audit/tests/test_models.py`
- [X] T003 [P] [US1] Criar testes de formulário, inclusão autorizada, rejeições, mensagens e duplicidade em `src/apps/workspaces/tests/test_views.py`

### Implementação da História 1

- [X] T004 [US1] Criar `AuditEvent` com ator, workspace, conta associada, ação e instante em `src/apps/audit/models.py` e gerar `src/apps/audit/migrations/0001_initial.py`
- [X] T005 [US1] Implementar formulário que remove espaços, procura e-mail sem diferenciar caixa, exige conta ativa e rejeita correspondência ambígua em `src/apps/workspaces/forms.py`
- [X] T006 [US1] Implementar inclusão autorizada, transação de associação/auditoria, tratamento de conflito e rota `workspaces:member-add` em `src/apps/workspaces/views.py` e `src/apps/workspaces/urls.py`
- [X] T007 [US1] Exibir o formulário somente para quem pode gerir o workspace e atualizar a lista após inclusão em `src/apps/workspaces/views.py` e `src/templates/workspaces/workspace_detail.html`
- [X] T008 [US1] Executar os testes focados de workspace e auditoria em `src/apps/workspaces/tests/test_views.py` e `src/apps/audit/tests/test_models.py`

---

## Fase 4: História 2 - Voltar à tela anterior (Prioridade: P1)

**Objetivo**: Disponibilizar em cada tela autenticada um ícone de retorno acessível, com navegação interna segura e fallback contextual.

**Teste independente**: Verificar o controle nas nove telas autenticadas, o retorno via histórico interno e o fallback correto ao abrir uma tela diretamente ou após navegação externa.

### Testes da História 2

- [X] T009 [P] [US2] Criar testes de presença do ícone, nome acessível e destino contextual para as telas autenticadas em `src/apps/dashboard/tests/test_back_navigation.py`

### Implementação da História 2

- [X] T010 [US2] Implementar ícone-only, rótulo acessível, tooltip, foco visível, histórico limitado à mesma origem e fallbacks contextuais no layout e templates autenticados em `src/templates/base.html`, `src/templates/dashboard/dashboard.html`, `src/templates/tasks/task_list.html`, `src/templates/tasks/task_form.html`, `src/templates/workspaces/workspace_list.html`, `src/templates/workspaces/workspace_form.html`, `src/templates/workspaces/workspace_detail.html`, `src/templates/scheduling/calendar.html`, `src/templates/scheduling/schedule_form.html` e `src/templates/scheduling/occurrence_detail.html`
- [X] T011 [US2] Executar testes de navegação e verificar os nove cenários de renderização/fallback conforme `src/apps/dashboard/tests/test_back_navigation.py` e `specs/002-workspace-members-navigation/quickstart.md`

---

## Fase 5: História 3 - Reconhecer ações pelos botões (Prioridade: P2)

**Objetivo**: Padronizar cores semânticas e estados de interação dos botões nas telas autenticadas sem perder legibilidade ou identidade visual.

**Teste independente**: Comparar botões principais, secundários e destrutivos nas telas autenticadas e verificar contraste e estados normal, hover, foco e desabilitado em desktop e mobile.

### Implementação da História 3

- [X] T012 [US3] Definir tokens e estilos compartilhados de botões principais, secundários e destrutivos, incluindo hover, foco e desabilitado em `src/static/css/auth.css`
- [X] T013 [US3] Substituir estilos de cor divergentes por classes semânticas nos templates autenticados em `src/templates/base.html`, `src/templates/dashboard/dashboard.html`, `src/templates/tasks/task_list.html`, `src/templates/tasks/task_form.html`, `src/templates/workspaces/workspace_list.html`, `src/templates/workspaces/workspace_form.html`, `src/templates/workspaces/workspace_detail.html`, `src/templates/scheduling/calendar.html`, `src/templates/scheduling/schedule_form.html` e `src/templates/scheduling/occurrence_detail.html`
- [X] T014 [US3] Verificar que `src/static/css/auth.css` contém estilos distintos para hover, foco e desabilitado e que os pares de cor atendem aos contrastes de `specs/002-workspace-members-navigation/spec.md`

---

## Fase 6: Polimento e validação transversal

- [X] T015 [P] Atualizar `docs/authorization.md` para documentar que somente proprietária/gestora pode adicionar membros, sem declarar concluído o modelo global de autorização
- [X] T016 Executar suíte completa, Ruff, verificação Django e checagem de migrações conforme `specs/002-workspace-members-navigation/quickstart.md`
- [X] T017 Revisar todas as tarefas, critérios da spec e resultado de validação visual em `specs/002-workspace-members-navigation/tasks.md` e `specs/002-workspace-members-navigation/quickstart.md`
- [X] T018 Permitir que apenas owner/gestor remova membro desativando o vínculo e registrando auditoria em `src/apps/workspaces/views.py`, `src/apps/workspaces/urls.py`, `src/apps/audit/models.py` e `src/templates/workspaces/workspace_detail.html`
- [X] T019 Restringir atribuição manual de ocorrência a owner/gestor no contexto, interface e POST e documentar os limites de autorização em `src/apps/scheduling/views.py`, `src/templates/scheduling/occurrence_detail.html` e `docs/authorization.md`
- [X] T020 Cobrir remoção, proteção do owner e atribuição de ocorrência por papel em `src/apps/workspaces/tests/test_views.py` e `src/apps/scheduling/tests/test_views.py`
- [X] T021 Gerar e aplicar a migração da ação de auditoria de remoção e executar os gates finais em `src/apps/audit/migrations/0002_alter_auditevent_action.py`

## Dependências e ordem de execução

### Dependências das fases

- Setup (Fase 1) precede as histórias; os arquivos ignore e dependências já existem, mas devem ser confirmados.
- Fundacional (Fase 2) não adiciona trabalho bloqueador.
- História 1 (Fase 3) pode ser implementada primeiro e constitui o MVP funcional.
- História 2 (Fase 4) segue a História 1 porque ambas atualizam a tela de workspace; suas regras de navegação são independentes da lógica de membros.
- História 3 (Fase 5) segue a História 2 porque ambas atualizam os mesmos templates.
- Polimento (Fase 6) depende das três histórias.

### Dependências entre tarefas

- T002 e T003 são independentes e precedem a implementação da História 1.
- T004 e T005 podem ser desenvolvidas em paralelo depois dos testes; T006 depende de ambas; T007 depende de T006; T008 valida a história completa.
- T009 precede T010; T011 valida o resultado de T010.
- T012 precede T013; T014 valida a aplicação visual.
- T015 é independente e pode ocorrer em paralelo com T012/T013; T016 e T017 fecham a entrega.

## Oportunidades de paralelismo

- História 1: T002 e T003 atuam em arquivos de teste diferentes; após ambos falharem como esperado, T004 e T005 também atuam em arquivos distintos.
- Polimento: T015 altera apenas documentação e pode ocorrer em paralelo à implementação visual da História 3.
- As histórias não são paralelas neste repositório, pois navegação e cores compartilham templates com a tela de workspace e entre si.

## Estratégia de implementação

1. Confirmar setup existente e executar TDD da inclusão de membros e auditoria.
2. Entregar a História 1 como MVP e validar isolamento por permissão, unicidade e atomicidade.
3. Implementar o ícone e os fallbacks da História 2 em todas as telas autenticadas.
4. Aplicar a paleta semântica da História 3 e validar estados visuais e contraste.
5. Executar documentação, suíte completa, Ruff, Django check e checagem de migrações.