# Feature Specification: Atribuição em Recorrências

**Feature Branch**: `001-atribuicao-recorrencias`

**Created**: 2026-11-14

**Status**: Draft

**Input**: User description: "Fechar a ponte entre recorrências e execução real: incluir o proprietário e membros ativos do espaço como responsáveis; impedir atribuições duplicadas por membro; permitir responsável padrão ao criar recorrência; mostrar atribuições no detalhe da ocorrência; validar membros elegíveis; criar ou atualizar a ação de atribuição; e testar atribuição válida, rejeição de membro externo e bloqueio de duplicidade."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Definir responsável padrão da recorrência (Priority: P1)

Uma pessoa autorizada a criar tarefas configura uma recorrência e escolhe, opcionalmente, um responsável padrão entre o proprietário e os membros ativos do espaço. As ocorrências geradas para essa recorrência passam a apresentar uma atribuição para esse responsável. Sem responsável padrão, as ocorrências são geradas sem atribuição automática.

**Why this priority**: A atribuição desde a criação conecta o planejamento recorrente à execução de cada ocorrência.

**Independent Test**: Criar uma recorrência com responsável válido e verificar que suas ocorrências geradas incluem essa atribuição; repetir sem responsável e verificar que nenhuma atribuição padrão é criada.

**Acceptance Scenarios**:

1. **Given** uma tarefa em um espaço com proprietário e membro ativo, **When** uma pessoa autorizada cria uma recorrência e escolhe o membro como responsável padrão, **Then** cada ocorrência gerada para a recorrência recebe uma única atribuição para esse membro.
2. **Given** uma recorrência criada sem responsável padrão, **When** suas ocorrências são geradas, **Then** elas permanecem sem atribuição automática.
3. **Given** o proprietário também aparece como membro ativo do espaço, **When** a lista de responsáveis padrão é apresentada, **Then** o proprietário aparece uma única vez.

---

### User Story 2 - Atribuir responsável a uma ocorrência (Priority: P1)

Uma pessoa com permissão para gerenciar tarefas do espaço adiciona um responsável elegível a uma ocorrência existente. A pessoa pode escolher o proprietário ou um membro ativo do espaço; alguém de fora ou com vínculo inativo não pode ser atribuído. Repetir uma atribuição existente não cria outra atribuição para o mesmo membro.

**Why this priority**: A atribuição manual cobre ocorrências que ficaram sem responsável padrão e impede que a execução seja associada a pessoas sem vínculo válido.

**Independent Test**: Atribuir um membro ativo com sucesso, tentar atribuir uma pessoa externa e repetir a atribuição do membro; confirmar, respectivamente, uma atribuição criada, nenhuma atribuição externa e nenhuma duplicata.

**Acceptance Scenarios**:

1. **Given** uma ocorrência e um membro ativo do espaço ainda não atribuído, **When** uma pessoa autorizada o seleciona, **Then** a atribuição é registrada e a pessoa recebe confirmação.
2. **Given** uma ocorrência e uma pessoa sem vínculo ativo com o espaço que não é seu proprietário, **When** alguém tenta atribuí-la, **Then** a solicitação é rejeitada e nenhuma atribuição é registrada.
3. **Given** uma ocorrência que já tem atribuição para um membro, **When** alguém tenta atribuir o mesmo membro novamente, **Then** a duplicata é bloqueada, a atribuição existente é preservada e a pessoa recebe retorno informativo.
4. **Given** uma pessoa sem permissão para gerenciar tarefas do espaço, **When** ela tenta alterar atribuições, **Then** a ação é negada e as atribuições permanecem inalteradas.

---

### User Story 3 - Consultar atribuição e executar ocorrência (Priority: P2)

Uma pessoa consulta o detalhe da ocorrência para identificar seus responsáveis e o estado de cada atribuição. Um responsável pendente consegue registrar sua própria execução e acompanhar a conclusão correspondente à sua atribuição.

**Why this priority**: A atribuição só fecha o ciclo de recorrência quando fica visível na ocorrência e orienta quem pode registrar a execução.

**Independent Test**: Abrir o detalhe de uma ocorrência atribuída, conferir os responsáveis e estados apresentados, registrar a execução como responsável e verificar que a execução e a conclusão pertencem à sua atribuição.

**Acceptance Scenarios**:

1. **Given** uma ocorrência com um ou mais responsáveis, **When** uma pessoa autorizada abre seu detalhe, **Then** cada responsável e o estado de sua atribuição são exibidos.
2. **Given** uma ocorrência com atribuição pendente para a pessoa autenticada, **When** ela abre o detalhe e registra sua execução, **Then** o registro fica associado à sua atribuição e ela pode concluir somente a própria atribuição.
3. **Given** uma ocorrência sem atribuições, **When** uma pessoa autorizada abre seu detalhe, **Then** a interface informa que não há responsáveis atribuídos.

### Edge Cases

- O proprietário também possui uma associação ativa de membro: deve ser listado uma única vez.
- Um membro é desativado depois de já ter sido atribuído: a atribuição e seu histórico existentes permanecem; novas atribuições devem validar o vínculo ativo no momento da ação.
- A recorrência não gera ocorrências no período aplicável: nenhuma atribuição padrão é criada sem uma ocorrência correspondente.
- Duas tentativas de atribuir o mesmo membro à mesma ocorrência chegam repetidamente: deve permanecer no máximo uma atribuição para esse par.
- Uma pessoa tem vínculo ativo em outro espaço, mas não no espaço da ocorrência: ela não é elegível para essa ocorrência.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Ao criar uma recorrência, o sistema MUST oferecer como responsáveis o proprietário do espaço e seus membros ativos, sem repetir pessoas que tenham mais de um desses vínculos.
- **FR-002**: O sistema MUST permitir que a pessoa autorizada escolha um responsável padrão opcional ao criar uma recorrência.
- **FR-003**: Quando houver responsável padrão, o sistema MUST atribuí-lo uma única vez a cada ocorrência gerada para a recorrência; quando não houver, MUST manter as ocorrências sem atribuição automática.
- **FR-004**: O sistema MUST permitir que pessoas autorizadas a gerenciar tarefas do espaço adicionem à ocorrência o proprietário ou um membro ativo daquele mesmo espaço.
- **FR-005**: O sistema MUST rejeitar uma atribuição a uma pessoa que não seja o proprietário nem membro ativo do espaço da ocorrência, sem persistir a atribuição rejeitada.
- **FR-006**: O sistema MUST impedir mais de uma atribuição da mesma pessoa à mesma ocorrência, inclusive em tentativas repetidas ou concorrentes, preservando a atribuição existente.
- **FR-007**: Ao tentar repetir uma atribuição já existente, o sistema MUST informar que a pessoa já está atribuída, sem criar um segundo registro.
- **FR-008**: O detalhe da ocorrência MUST exibir seus responsáveis e o estado individual de cada atribuição, ou informar quando não houver atribuições.
- **FR-009**: Uma pessoa atribuída MUST poder registrar a execução e concluir somente a própria atribuição, sem alterar a execução ou a conclusão de outros responsáveis.
- **FR-010**: O sistema MUST restringir a alteração de atribuições às pessoas autorizadas a gerenciar tarefas no espaço e MUST validar a elegibilidade no servidor, inclusive quando a solicitação não vier da interface de seleção.

### Key Entities *(include if feature involves data)*

- **Espaço**: Contexto que possui um proprietário e associações de membros com estado ativo ou inativo.
- **Recorrência**: Regra que gera ocorrências e pode ter um responsável padrão opcional.
- **Ocorrência**: Instância datada de uma tarefa recorrente ou avulsa que pode receber responsáveis.
- **Atribuição**: Relação entre uma ocorrência e uma pessoa responsável, com estado próprio de execução e conclusão; uma pessoa pode ter no máximo uma atribuição por ocorrência.
- **Registro de execução**: Evidência de execução vinculada à atribuição de uma pessoa para uma ocorrência.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em todos os casos de aceitação de criação de recorrência, 100% das ocorrências geradas recebem a atribuição padrão escolhida, sem atribuições automáticas quando nenhuma pessoa for escolhida.
- **SC-002**: Em 100% das tentativas de atribuição testadas, somente o proprietário ou membros ativos do espaço da ocorrência são aceitos; tentativas com pessoas externas ou inativas não criam atribuições.
- **SC-003**: Para qualquer ocorrência e pessoa responsável, o total de atribuições permanece em no máximo uma, inclusive após pelo menos duas tentativas de atribuição da mesma pessoa.
- **SC-004**: Uma pessoa responsável consegue identificar sua atribuição no detalhe da ocorrência e registrar a própria execução sem concluir atribuições de outros responsáveis.

## Assumptions

- O proprietário é elegível para atribuição independentemente de possuir uma associação explícita de membro.
- Qualquer membro ativo pode ser responsável; o papel do membro não restringe a elegibilidade. A permissão para efetuar a atribuição continua sujeita às permissões de gerenciamento de tarefas do espaço.
- A validade do vínculo é verificada no momento da seleção e da atribuição. Desativar um membro não apaga atribuições nem execuções já registradas.
- O responsável padrão se aplica às ocorrências geradas pela recorrência criada e não altera retroativamente atribuições de outras ocorrências.
- Esta entrega não inclui notificações, auditoria, edição ou remoção de atribuições existentes.