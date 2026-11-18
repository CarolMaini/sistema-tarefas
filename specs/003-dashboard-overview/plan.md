# Implementation Plan: Dashboard de Acompanhamento Pessoal

**Branch**: 003-dashboard-overview-spec | **Date**: 2026-11-18 | **Spec**: spec.md

## Summary

Substituir os contadores provisórios do Dashboard por consultas reais às atribuições do usuário autenticado e apresentar até 10 próximas ocorrências atribuídas a ele. Reutilizar Workspace, TaskAssignment, TaskOccurrence e as rotas existentes; não criar migrações nem alterar regras de negócio.

## Technical Context

- Language: Python 3.12
- Framework: Django, Django Templates
- Data: modelos existentes de workspaces, tarefas, atribuições e ocorrências
- Tests: pytest, pytest-django, Django test client
- Quality: Ruff, Django check, makemigrations --check --dry-run, suíte completa
- Scope: src/apps/dashboard/views.py, src/apps/dashboard/tests/, src/templates/dashboard/dashboard.html

## Design Decisions

1. O escopo de acesso é calculado pelo mesmo critério já usado no Dashboard: workspace ativo cujo owner é o usuário ou em que há membership ativa.
2. As métricas são pessoais: contam apenas atribuições cujo user_id corresponde ao usuário autenticado.
3. Pendência é TaskAssignment.Status.PENDING; concluída/cancelada são excluídas.
4. Próximas ações exigem atribuição pendente, ocorrência OPEN, workspace ativo e data de hoje até hoje + 7 dias, inclusive.
5. A lista é ordenada por data e título e limitada a 10 itens; a contagem não é limitada.
6. Cada item usa a rota existente scheduling:occurrence-detail com workspace e ocorrência correspondentes.
7. Não adicionar score, notificações, filtros ou novos modelos nesta feature.

## Constitution Check

- Simplicidade: PASS — consultas diretas e sem dependências novas.
- Segurança: PASS — filtro de usuário e workspaces acessíveis no servidor.
- Integridade: PASS — não altera atribuições, ocorrências ou regras de domínio.
- Qualidade: PASS — testes de isolamento, limites temporais e estados vazios antes da implementação.

## Project Structure

src/apps/dashboard/\n├── views.py\n└── tests/\n    ├── test_dashboard.py\n    └── test_back_navigation.py\nsrc/templates/dashboard/\n└── dashboard.html\nspecs/003-dashboard-overview/\n├── spec.md\n├── plan.md\n├── tasks.md\n└── quickstart.md

## Risks

- Contagens duplicadas se forem agregadas por join de memberships sem distinct(); usar queryset de workspaces e filtrar atribuições por workspace.
- Exposição indevida por filtrar apenas usuário sem validar workspace ativo; cobrir explicitamente workspace inativo e membro inativo.
- Diferenças de fuso ao calcular hoje; usar django.utils.timezone.localdate().
