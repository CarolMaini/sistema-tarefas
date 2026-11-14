# Implementation Plan: Atribuição em Recorrências

**Branch**: `001-atribuicao-recorrencias` | **Date**: 2026-11-14 | **Spec**: [spec.md](spec.md)

**Input**: [Feature specification](spec.md)

## Summary

Fechar o fluxo entre regras de recorrência e execução por responsável. O projeto já possui seleção de
responsável padrão no formulário de criação, geração idempotente de ocorrências, atribuição manual,
exibição de responsáveis no detalhe e uma constraint única por ocorrência/usuário. A lacuna principal
é que o responsável padrão não é persistido na `ScheduleRule`, portanto o gerador não pode aplicá-lo a
ocorrências produzidas depois da requisição inicial. O plano persiste essa preferência na regra,
reutiliza `generate_occurrences`, centraliza elegibilidade no domínio de `Workspace` e faz a atribuição
manual usar criação idempotente apoiada pela constraint atual.

## Technical Context

**Language/Version**: Python 3.12 (`>=3.12,<3.13`)

**Primary Dependencies**: Django 6.1.2; Django Templates; pytest, pytest-django e Ruff

**Storage**: PostgreSQL como banco primário; SQLite em `setup.settings.local` para desenvolvimento e
testes locais

**Testing**: pytest-django; testes focados de scheduling, workspace e integridade de atribuições

**Target Platform**: Aplicação web Django executada em servidor Linux ou ambiente local de desenvolvimento

**Project Type**: Monólito modular Django, com apps em `src/apps/` e templates server-rendered em
`src/templates/`

**Performance Goals**: Não há meta de desempenho específica para este fluxo; preservar o número limitado
de consultas e as transações já usadas na geração

**Constraints**: Não adicionar dependências; validar autorização no servidor; manter histórico de
atribuições e execuções; elegibilidade significa proprietário ou membro ativo do mesmo workspace;
atribuições continuam únicas por ocorrência e usuário; não incluir notificações ou auditoria

**Scale/Scope**: Uma regra pode gerar várias ocorrências por chamada; alteração restrita ao app
`scheduling`, à consulta de elegibilidade do app `workspaces` e aos testes correspondentes

## Diagnóstico da implementação atual

- `ScheduleRule` em `src/apps/scheduling/models.py` guarda a regra e suas datas, mas não o responsável
  padrão.
- `ScheduleRuleForm` em `src/apps/scheduling/forms.py` já limita as opções ao proprietário e aos membros
  ativos, deduplicando IDs. O campo opcional `assignee`, contudo, não corresponde a um campo persistido.
- `ScheduleRuleCreateView` em `src/apps/scheduling/views.py` salva a regra, chama o gerador e cria
  atribuições do responsável em um segundo passo, limitado ao lote inicial.
- `generate_occurrences` em `src/apps/scheduling/services.py` gera datas semanal, quinzenal e mensalmente
  em transação e usa `get_or_create` para ocorrência única por tarefa/data. Se a ocorrência existe sem
  regra, associa-a; se já pertence a outra regra, preserva o vínculo. O serviço ainda não cria atribuições.
- `Workspace` e `WorkspaceMembership` em `src/apps/workspaces/models.py` definem proprietário,
  associação ativa e autorização do ator. A elegibilidade de responsável é repetida no formulário,
  contexto do detalhe e view de atribuição.
- `TaskOccurrenceDetailView` já entrega responsáveis, estado, formulário de execução e lista elegível;
  `occurrence_detail.html` já apresenta essas atribuições e a mensagem para lista vazia.
- `TaskOccurrenceAssignView` e a rota `scheduling:occurrence-assign` já implementam atribuição POST,
  permissão `can_create_tasks` e rejeição de usuário fora do espaço. A sequência `exists()` seguida de
  `create()` pode competir sob requisições simultâneas.
- `TaskAssignment` em `src/apps/tasks/models.py` já impõe `UniqueConstraint(occurrence, user)` e possui
  estados/histórico de conclusão. A execução é associada à atribuição do usuário autenticado, e a
  conclusão só é permitida ao próprio responsável após registrar execução.
- `test_services.py` cobre datas e idempotência de ocorrências; `test_views.py` cobre atribuição válida,
  padrão inicial e execução. Ainda faltam casos de usuário externo/inativo, atribuição repetida, padrão
  persistido em geração posterior e apresentação dos dados de atribuição no detalhe.

## Decisões arquiteturais

1. Persistir `ScheduleRule.default_assignee` como FK opcional para `settings.AUTH_USER_MODEL`, anulável,
   com `on_delete=PROTECT`, seguindo as referências de usuários já protegidas nos modelos de tarefas e
   recorrências. Regras existentes recebem `NULL` na migration; não haverá backfill.
2. Colocar em `Workspace` métodos reutilizáveis para obter os usuários atribuíveis e verificar se um
   usuário é atribuível. A regra é proprietário ou membro ativo; o papel do membro não restringe a
   elegibilidade. A autorização do ator permanece separada e usa `can_create_tasks`.
3. Atualizar o `ModelChoiceField` existente para persistir `default_assignee`. A interface mantém o
   rótulo “Responsável padrão”; o nome interno submetido passa a refletir o campo persistido.
4. Fazer `generate_occurrences` aplicar o responsável padrão com `TaskAssignment.get_or_create` dentro
   da transação do gerador. Aplicar somente às ocorrências criadas, associadas pela primeira vez ou já
   vinculadas à regra atual; não alterar ocorrência vinculada a outra regra e não substituir estado ou
   histórico de atribuição existente.
5. Usar a mesma operação idempotente de domínio na atribuição manual. Uma repetição retorna a atribuição
   existente e informa a pessoa; a constraint atual permanece como proteção final contra concorrência.
6. Manter as rotas atuais e templates atuais: a seleção na criação, a ação POST da ocorrência, a lista
   de atribuições/estados, o retorno de duplicidade via mensagens e o registro/conclusão de execução já
   estão implementados. Acrescentar testes de regressão para confirmar esses contratos, não reescrever
   a UI.
7. Não criar API JSON nem modelo de atribuição alternativo. O contrato de interface é HTML server-side
   e fica documentado em `contracts/occurrence-assignment.md`.

## Regras de negócio e validações

- Responsáveis elegíveis: proprietário ou membro ativo do mesmo workspace. A lista deve ser distinta,
  inclusive quando o proprietário também tem associação de membro.
- A seleção do formulário restringe a escolha, mas as operações de atribuição e geração revalidam a
  elegibilidade no servidor.
- Somente ator autorizado por `Workspace.can_create_tasks()` pode criar regra ou atribuir manualmente.
- Responsável padrão ausente significa que o gerador não cria atribuições automáticas.
- Responsável padrão que deixou de ser elegível não recebe novas atribuições; a ocorrência ainda é
  gerada, e atribuições anteriores não são removidas nem alteradas. Após reativação, futuras ocorrências
  podem voltar a receber o responsável.
- `get_or_create` mais a constraint existente mantém no máximo uma atribuição por par e preserva o
  status de atribuição já existente, inclusive cancelada ou concluída.
- Uma ocorrência avulsa sem regra pode ser associada à regra que a gera, conforme comportamento atual.
  Uma ocorrência já associada a outra regra não é reassociada nem recebe o padrão da regra corrente.
- Usuário externo ou com vínculo inativo é rejeitado sem persistir atribuição. Mensagens e status HTTP
  seguem o padrão atual da view de atribuição; nenhuma rota nova será criada.
- Atribuições são independentes por responsável. Registro e conclusão continuam restritos à atribuição
  do usuário autenticado e não modificam atribuições de outros responsáveis.

## Arquivos a modificar

### Aplicação

- `src/apps/scheduling/models.py`: campo opcional de responsável padrão em `ScheduleRule`.
- `src/apps/scheduling/forms.py`: queryset pelo método de elegibilidade de `Workspace` e persistência do
  campo no formulário.
- `src/apps/scheduling/services.py`: operação reutilizável de atribuição elegível/idempotente e aplicação
  do padrão durante a geração.
- `src/apps/scheduling/views.py`: remover criação em lote de atribuições após a geração, usar a operação
  idempotente na rota manual e reutilizar a lista elegível no detalhe.
- `src/apps/workspaces/models.py`: centralizar consulta e validação de usuários atribuíveis.
- `src/apps/scheduling/migrations/0004_schedulerule_default_assignee.py`: migration anulável; nome exato
  será o gerado pela ferramenta de migrations.

### Testes

- `src/apps/scheduling/tests/test_services.py`: padrão persistido, ausência de padrão, geração posterior,
  repetição, estado existente, padrão inelegível e colisão com ocorrência de outra regra.
- `src/apps/scheduling/tests/test_views.py`: opções distintas elegíveis, atribuição válida, rejeição de
  externo/inativo, repetição informativa, autorização, detalhe e execução por responsável.
- `src/apps/workspaces/tests/test_models.py`: conjunto elegível distinto e validação de proprietário,
  membro ativo, membro inativo e usuário externo.

## Arquivos novos

- Nenhum arquivo novo de aplicação além da migration. Os documentos de planejamento são artefatos desta
  feature; não há necessidade de nova rota, template ou componente.

## Estratégia de testes

1. Testes unitários de workspace confirmam que o proprietário e membros ativos compõem a lista sem
   duplicidade; usuários externos e associações inativas são inelegíveis.
2. Testes de serviço verificam criação de ocorrências com padrão, sem padrão, geração em intervalos
   posteriores, repetição sem duplicata e preservação de atribuição/status existente.
3. Testes de colisão garantem que uma ocorrência já vinculada a outra regra não recebe o responsável da
   regra corrente; ocorrência avulsa associada pela primeira vez segue o padrão.
4. Testes de view submetem atribuições válidas, externas, inativas e repetidas; verificam persistência,
   mensagem e ausência de duplicata, além do bloqueio por permissão.
5. Testes de detalhe confirmam nome/estado da atribuição, lista vazia, registro de execução pelo próprio
   responsável e conclusão sem alterar as atribuições dos demais.
6. A constraint única existente continua sendo validada pelo teste de modelo de `TaskAssignment`; a
   repetição no serviço/view cobre idempotência. Testes de concorrência em PostgreSQL podem ser
   adicionados se a suíte CI oferecer execução paralela com esse banco; SQLite local não deve ser usado
   para afirmar comportamento de concorrência.

## Riscos e impactos em funcionalidades existentes

- A migration é aditiva e todas as regras existentes mantêm `default_assignee=NULL`; portanto não há
  atribuição retroativa nem alteração de ocorrências existentes.
- `PROTECT` impede excluir diretamente um usuário referenciado como padrão. Isso mantém explícita a
  preferência e é consistente com referências de criador/responsável já protegidas no domínio.
- Uma associação pode ser desativada entre a gravação da regra e a geração: a ocorrência continua sendo
  criada sem a nova atribuição. Não se apagam atribuições existentes.
- A constraint de tarefa/data permite colisões com ocorrências avulsas ou de outra regra. A geração deve
  preservar o vínculo existente e só aplicar o padrão quando a ocorrência pertence à regra gerada.
- A constraint única resolve a integridade sob duplicidade concorrente; o tratamento de `get_or_create`
  deve continuar compatível com PostgreSQL. SQLite local cobre repetição sequencial, não corrida.
- O campo POST do responsável padrão passa de `assignee` transitório a `default_assignee` persistido.
  O template renderiza os campos do formulário automaticamente; testes e qualquer cliente interno que
  submeta esse formulário devem usar o novo nome.
- Não há impacto esperado em notificações, auditoria, calendário ou regras de recorrência existentes.

## Constitution Check

**Gate antes da pesquisa**: PASS. A stack configurada e a Constitution estão alinhadas em Python 3.12
(`>=3.12,<3.13`) e Django 6.1.2. O plano preserva a arquitetura modular, usa CBVs e serviço existente,
mantém autenticação/autorização no servidor, não adiciona dependências e prevê testes de regras,
permissões e integridade.

**Gate depois do design**: PASS. A migration é aditiva, as alterações ficam nas fronteiras existentes
de scheduling/workspaces, as rotas e templates são reutilizados, e atribuições/histórico existentes
permanecem preservados. A conformidade de implementação deverá ser confirmada por pytest, Ruff,
`manage.py check` e verificação de migrations antes de considerar a feature concluída.

## Project Structure

### Documentação desta feature

```text
specs/001-atribuicao-recorrencias/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── occurrence-assignment.md
└── tasks.md
```

### Código existente envolvido

```text
src/apps/
├── scheduling/
│   ├── forms.py
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   ├── migrations/
│   └── tests/
├── tasks/
│   └── models.py                 # constraint e execução reutilizadas; sem mudança prevista
└── workspaces/
    ├── models.py
    └── tests/test_models.py

src/templates/scheduling/
├── schedule_form.html            # renderiza campos do formulário existente; sem mudança prevista
└── occurrence_detail.html        # já exibe atribuições; sem mudança prevista
```

**Structure Decision**: Preservar o monólito Django atual. Alterações de regra e UI ficam no app
`scheduling`; a elegibilidade é centralizada em `Workspace`, que é dono do proprietário e das
associações. `TaskAssignment` permanece no app `tasks`. Não criar serviço, API, app ou camada de
repositório adicional.

## Complexity Tracking

Não há violações da Constitution nem novas dependências ou camadas que precisem de justificativa.
