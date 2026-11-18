# Tasks: Dashboard de Acompanhamento Pessoal

**Input**: spec.md, plan.md
**Tests**: obrigatórios para contagens, isolamento, datas, estados e links.

## Phase 1: Tests

- [ ] T001 [P] Criar testes de autenticação, contagem de atribuições pendentes e exclusão de concluídas/canceladas em src/apps/dashboard/tests/test_dashboard.py.
- [ ] T002 [P] Criar testes de isolamento para workspace alheio, membership inativa e workspace inativo em src/apps/dashboard/tests/test_dashboard.py.
- [ ] T003 [P] Criar testes de janela temporal, ocorrência cancelada, ordenação, limite de 10 itens e links corretos em src/apps/dashboard/tests/test_dashboard.py.
- [ ] T004 [P] Criar testes dos estados vazios sem workspace, sem pendências e sem próximas ocorrências em src/apps/dashboard/tests/test_dashboard.py.

## Phase 2: Implementation

- [ ] T005 Implementar consultas seguras e context data reais em src/apps/dashboard/views.py, usando timezone.localdate() e evitando N+1.
- [ ] T006 Substituir placeholders e renderizar indicadores, lista de próximas atribuições e estados vazios em src/templates/dashboard/dashboard.html.

## Phase 3: Validation

- [ ] T007 Executar testes focados do Dashboard e os testes existentes de navegação.
- [ ] T008 Executar Ruff, Django check, makemigrations --check --dry-run e suíte completa.
- [ ] T009 Revisar isolamento de dados, ausência de migrations e atualizar esta lista com resultados reais.

## Dependencies

T001–T004 precedem T005. T005 precede T006. T007–T009 encerram a entrega.
