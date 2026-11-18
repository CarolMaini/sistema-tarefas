# Feature Specification: Dashboard de Acompanhamento Pessoal

**Feature Branch**: 003-dashboard-overview
**Created**: 2026-11-18
**Status**: Draft

## Contexto

O Dashboard atual já é a rota inicial autenticada, mas seus indicadores de tarefas pendentes e próximas ocorrências são valores fixos em zero. A área de próximas ações é um placeholder. Esta entrega transforma o painel em uma visão real e confiável do trabalho atribuído à pessoa autenticada, reutilizando os modelos existentes.

## Objetivo e limites

Entregar um resumo pessoal de atribuições e ocorrências futuras em todos os workspaces ativos aos quais a pessoa tem acesso. Não criar modelos ou migrações para pontuação, notificações, metas ou relatórios. Não alterar as regras de autorização ou o fluxo de recorrências.

## User Stories

### US1 — Consultar indicadores pessoais (P1)

Como pessoa autenticada, quero ver quantas atribuições minhas estão pendentes e quantas ocorrências atribuídas a mim estão próximas, para entender rapidamente o que exige minha atenção.

**Critérios de aceite**
1. Os indicadores são calculados a partir de TaskAssignment e TaskOccurrence, nunca valores fixos.
2. A consulta considera apenas atribuições do usuário autenticado em workspaces ativos e acessíveis.
3. Atribuições concluídas ou canceladas não entram na contagem de pendências.
4. Ocorrências canceladas e ocorrências passadas não entram na contagem de próximas ocorrências.
5. O limite temporal de próximas é explícito e consistente: hoje até os próximos 7 dias, inclusive, usando a data local do Django.
6. O painel não conta a mesma ocorrência mais de uma vez para o mesmo usuário.

### US2 — Consultar próximas atribuições (P1)

Como pessoa autenticada, quero ver uma lista das próximas ocorrências atribuídas a mim e abrir seu detalhe, para acessar diretamente o trabalho que preciso executar.

**Critérios de aceite**
1. A lista contém somente atribuições pendentes do usuário autenticado.
2. Cada item mostra título da tarefa, workspace e data agendada.
3. Cada item leva ao detalhe da ocorrência dentro do workspace correspondente.
4. A lista é ordenada primeiro pela data agendada e depois pelo título da tarefa.
5. A lista é limitada a 10 itens; o indicador continua refletindo o total dentro da janela de 7 dias.
6. Nenhuma tarefa ou ocorrência de workspace alheio ou inativo é exposta.

### US3 — Tratar ausência de dados (P2)

Como pessoa sem atribuições próximas, quero receber uma mensagem clara e útil, sem indicadores enganosos ou erros de renderização.

**Critérios de aceite**
1. Sem workspaces, o painel explica como começar criando ou entrando em um espaço.
2. Com workspaces mas sem atribuições pendentes, o painel mostra estado vazio específico.
3. Sem ocorrências nos próximos 7 dias, a lista informa que não há próximas ações.
4. Os indicadores mostram zero apenas quando o resultado real da consulta for zero.

## Requisitos funcionais

- FR-001: O dashboard deve exigir autenticação.
- FR-002: O dashboard deve calcular atribuições pendentes do usuário atual, excluindo status concluído e cancelado.
- FR-003: O dashboard deve considerar somente workspaces ativos em que o usuário seja proprietário ou membro ativo.
- FR-004: O dashboard deve contar ocorrências abertas atribuídas ao usuário com data entre hoje e hoje + 7 dias, inclusive.
- FR-005: O dashboard deve listar no máximo 10 próximas atribuições pendentes com links para os detalhes existentes.
- FR-006: Consultas e links devem respeitar o escopo de workspace e as permissões já implementadas.
- FR-007: O dashboard deve apresentar estados vazios distintos e não usar dados fictícios.
- FR-008: A implementação deve reutilizar modelos e constraints existentes, sem adicionar modelos, campos ou migrações.

## Fora de escopo

- Pontuação, ranking, gamificação e metas.
- Central de notificações e envio de e-mails.
- Gráficos históricos, exportação e relatórios.
- Seleção persistente de workspace ativo.
- Alterações em permissões, atribuição, recorrência ou execução.
- Publicação em produção.

## Requisitos não funcionais

- Consultas devem evitar N+1, usando select_related/consultas agregadas quando apropriado.
- Nenhuma informação de outro usuário ou workspace inacessível pode ser exibida.
- Cobertura automatizada para autenticação, isolamento, limites temporais, status, ordenação, limite de itens e estados vazios.
- Manter compatibilidade com Python 3.12, Django e padrões existentes do projeto.

## Success Criteria

- SC-001: 100% dos cenários de aceitação de contagem passam nos testes automatizados.
- SC-002: 100% dos testes de isolamento confirmam que dados de workspaces alheios/inativos não aparecem.
- SC-003: A lista mostra no máximo 10 atribuições e todos os links levam à ocorrência correta.
- SC-004: Ruff, Django checks, checagem de migrações e suíte completa passam no CI.
- SC-005: Nenhum modelo ou migration é adicionado nesta entrega.
