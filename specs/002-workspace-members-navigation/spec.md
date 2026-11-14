# Feature Specification: Membros e Navegação do Workspace

**Feature Branch**: `002-workspace-members-navigation`

**Created**: 2026-11-14

**Status**: Draft

**Input**: User description: "vamos iniciar uma nova implementação, para atualisar a tela do workspace para cadastrar novo membro, implemente tambem um botão de voltar, apenas o desenho do icon que seja funcional em cada uma das telas dentro do Organizador de Tarefas, apos login e ajuste as cores dos botões incluindo hovers e cores mais armoniozas com as descrições dos textos"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Adicionar membro ao workspace (Priority: P1)

Uma pessoa proprietária ou gestora de um workspace adiciona uma pessoa que já possui conta no Organizador de Tarefas. Ela informa o e-mail cadastrado, confirma a associação e passa a ver a nova pessoa na lista de membros do workspace.

**Why this priority**: O cadastro de membros é o objetivo principal do pedido e permite que outras pessoas participem do trabalho do workspace.

**Independent Test**: Como proprietária ou gestora, adicionar uma conta ativa ainda não associada e confirmar que ela aparece uma única vez na lista do workspace com acesso de colaboradora.

**Acceptance Scenarios**:

1. **Given** uma proprietária ou gestora em um workspace e uma conta ativa ainda não associada, **When** ela informa o e-mail cadastrado e confirma, **Then** a conta é associada como colaboradora e aparece na lista de membros.
2. **Given** uma pessoa sem permissão de gestão, **When** tenta adicionar uma conta ao workspace, **Then** a ação é negada e a lista de membros permanece inalterada.
3. **Given** um e-mail que não corresponde a uma conta ativa, **When** a pessoa gestora tenta adicioná-lo, **Then** o sistema informa que não foi possível localizar uma conta elegível e não cria uma associação.
4. **Given** uma conta que já é membro do workspace, **When** a pessoa gestora tenta adicioná-la novamente, **Then** nenhuma associação duplicada é criada e a pessoa recebe uma mensagem informativa.

---

### User Story 2 - Voltar à tela anterior (Priority: P1)

Uma pessoa autenticada encontra um controle de retorno composto apenas pelo ícone de voltar em cada tela do Organizador de Tarefas. Ao ativá-lo, retorna à tela anterior da aplicação; quando não há uma tela anterior disponível dentro da aplicação, chega a um destino seguro e relacionado ao contexto atual.

**Why this priority**: A navegação de retorno deve ser previsível em todo o fluxo autenticado, sem depender de um botão textual diferente em cada tela.

**Independent Test**: Abrir cada tela autenticada diretamente e a partir de outra tela; ativar o ícone e confirmar retorno à tela anterior ou, sem histórico interno, ao destino contextual previsto.

**Acceptance Scenarios**:

1. **Given** uma pessoa autenticada que chegou a uma tela a partir de outra tela interna, **When** ativa o ícone de voltar, **Then** retorna à tela interna anterior.
2. **Given** uma pessoa que abriu diretamente uma tela ou não possui histórico interno válido, **When** ativa o ícone, **Then** é levada à lista ou tela inicial apropriada ao contexto, sem sair do Organizador de Tarefas.
3. **Given** uma pessoa que navega por qualquer tela autenticada existente, **When** procura o controle de retorno, **Then** encontra o mesmo ícone, sem rótulo textual visível, com identificação acessível e indicação ao passar o ponteiro.

---

### User Story 3 - Reconhecer ações pelos botões (Priority: P2)

Uma pessoa autenticada reconhece com facilidade as ações principais, secundárias e destrutivas nas telas do sistema. Os botões mantêm cores coerentes com a intenção e com os textos próximos, e seus estados de interação continuam legíveis e distintos.

**Why this priority**: Uma linguagem visual consistente reduz dúvidas e evita que ações importantes pareçam iguais ou difíceis de ler.

**Independent Test**: Percorrer as telas autenticadas e verificar que botões com a mesma intenção compartilham estilo, que ações distintas são reconhecíveis, e que texto e ícones continuam legíveis nos estados normal, hover, foco e desabilitado.

**Acceptance Scenarios**:

1. **Given** botões de mesma intenção em telas autenticadas diferentes, **When** a pessoa os compara, **Then** eles usam tratamento visual consistente.
2. **Given** um botão em estado normal, **When** recebe hover ou foco, **Then** o estado muda de forma perceptível sem prejudicar a leitura do texto ou do ícone.
3. **Given** uma ação principal, secundária ou destrutiva, **When** ela é apresentada, **Then** sua aparência e seu texto comunicam a intenção sem depender exclusivamente da cor.

### Edge Cases

- O e-mail informado contém espaços ou diferença entre maiúsculas e minúsculas: a identificação da conta segue o mesmo padrão de e-mail usado pelo sistema.
- A conta encontrada está inativa: não pode ser adicionada ao workspace.
- A conta informada é a proprietária do workspace: o sistema não cria uma associação duplicada.
- Duas tentativas de adicionar a mesma conta ocorrem próximas uma da outra: permanece apenas uma associação por pessoa e workspace.
- Uma gestora tenta remover a pessoa proprietária: a operação é rejeitada e a associação da proprietária permanece ativa.
- Uma pessoa removida volta ao workspace no futuro: o vínculo anterior permanece inativo para preservar o histórico.
- Uma pessoa colaboradora tenta atribuir uma ocorrência a outra pessoa por envio direto: a atribuição não é criada.
- Uma pessoa acessa diretamente uma tela autenticada sem histórico de navegação interno: o ícone de retorno usa o destino contextual definido para aquela área.
- O usuário navega por um link externo antes de acionar voltar: o controle não o redireciona para fora do Organizador de Tarefas.
- O botão está desabilitado ou recebe foco por teclado: seu estado permanece distinguível e legível.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST apresentar, no detalhe do workspace, uma ação para adicionar uma pessoa que já tenha conta ativa no Organizador de Tarefas.
- **FR-002**: O sistema MUST permitir que somente a pessoa proprietária ou uma pessoa gestora ativa do workspace adicione membros.
- **FR-003**: O sistema MUST identificar a conta a adicionar pelo e-mail cadastrado e MUST associá-la ao workspace com o papel padrão de colaboradora.
- **FR-004**: O sistema MUST rejeitar e informar e-mails sem conta correspondente ou associados a contas inativas, sem alterar os membros do workspace.
- **FR-005**: O sistema MUST impedir associações duplicadas da mesma conta ao mesmo workspace e MUST apresentar retorno informativo quando a conta já for membro.
- **FR-006**: O sistema MUST exibir a nova associação na lista de membros após a inclusão bem-sucedida.
- **FR-007**: Todas as telas disponíveis a pessoas autenticadas MUST apresentar um controle de retorno composto visualmente apenas pelo ícone de voltar, sem texto visível.
- **FR-008**: O controle de retorno MUST retornar à tela interna anterior quando disponível e, caso contrário, MUST direcionar a pessoa a um destino interno relacionado ao contexto da tela atual.
- **FR-009**: O ícone de retorno MUST ter nome acessível e indicação descritiva ao passar o ponteiro, sem adicionar rótulo textual visível junto ao ícone.
- **FR-010**: Os botões das telas autenticadas MUST usar estilos consistentes conforme a intenção da ação, incluindo ações principais, secundárias e destrutivas quando presentes.
- **FR-011**: Os botões MUST apresentar estados distinguíveis de hover, foco e desabilitado, mantendo texto e ícones legíveis.
- **FR-012**: A intenção de uma ação MUST ser compreensível pelo texto ou ícone e não depender exclusivamente da cor.
- **FR-013**: Somente a pessoa proprietária ou uma gestora ativa MUST poder remover membros do workspace; colaboradoras e leitoras MUST ser impedidas no servidor.
- **FR-014**: Remover um membro MUST desativar sua associação, preservar o histórico e registrar um evento de auditoria; a pessoa proprietária MUST NOT ser removida.
- **FR-015**: Somente a pessoa proprietária ou uma gestora ativa MUST poder atribuir uma ocorrência a outra pessoa; colaboradoras MUST NOT obter essa permissão pela interface ou por envio direto.

### Key Entities *(include if feature involves data)*

- **Workspace**: Espaço de trabalho com uma pessoa proprietária e pessoas associadas com papéis e estados de participação.
- **Conta**: Pessoa com cadastro ativo no Organizador de Tarefas, identificada pelo e-mail registrado.
- **Associação de membro**: Vínculo entre uma conta e um workspace, com papel e estado de participação; cada conta pode ter no máximo um vínculo por workspace.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Uma pessoa autorizada consegue adicionar uma conta existente e ativa em até 1 minuto, e a nova pessoa aparece na lista do workspace em 100% dos testes de aceitação.
- **SC-002**: Em 100% das tentativas de inclusão testadas, contas inexistentes, inativas, já associadas ou solicitações sem permissão não geram uma associação indevida ou duplicada.
- **SC-003**: O controle de retorno está presente em 100% das telas autenticadas existentes e sempre conduz a uma tela interna válida nos testes de navegação direta e sequencial.
- **SC-004**: Em uma avaliação de compreensão, pelo menos 90% das pessoas identificam corretamente a ação principal, secundária ou destrutiva em exemplos das telas autenticadas.
- **SC-005**: O texto de botões atende ao contraste mínimo de 4,5:1 em tamanho normal e 3:1 em tamanho grande nos estados normal, hover, foco e desabilitado.
- **SC-006**: Em 100% das tentativas de remoção, apenas proprietária/gestora conseguem desativar a associação; toda remoção aceita deixa registro auditável e mantém o vínculo histórico.
- **SC-007**: Em 100% das tentativas testadas, colaboradoras não conseguem atribuir ocorrências a outras pessoas pela interface nem por envio direto.

## Assumptions

- “Cadastrar novo membro” significa associar ao workspace uma conta que já foi criada no Organizador de Tarefas; esta entrega não inclui convite por e-mail, criação de conta ou fluxo de inscrição.
- A inclusão concede o papel padrão de colaboradora; editar papéis ou reativar associações existentes não faz parte desta entrega. A remoção desativa o vínculo sem apagar seu histórico.
- A pessoa proprietária e pessoas gestoras ativas são as únicas autorizadas a adicionar membros, conforme as responsabilidades existentes para gestão do workspace.
- “Todas as telas após login” abrange as telas autenticadas existentes do dashboard, workspaces, tarefas, calendário e recorrências, incluindo formulários e detalhes.
- Quando não houver histórico interno, cada área usa como retorno a tela interna mais próxima e segura; páginas sem um contexto mais específico retornam à área principal autenticada.
- A harmonização de cores se aplica aos botões existentes nas telas autenticadas, preservando a distinção de intenção, legibilidade e identidade visual do produto.