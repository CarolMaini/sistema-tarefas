# Research: Membros e Navegação do Workspace

## Decisões

### Associação de uma conta existente

- **Decision**: Adicionar uma conta ativa informada pelo e-mail cadastrado, criando uma associação `WorkspaceMembership` com papel `COLLABORATOR`.
- **Rationale**: O cadastro próprio já tem e-mail único; o modelo de associação já contém papel, estado ativo e restrição única por workspace e pessoa. Isso atende ao fluxo solicitado sem convites, criação de contas ou alterações desnecessárias no modelo de associação.
- **Alternatives considered**: Criar convite por e-mail ou uma nova conta no fluxo do workspace; ambas ampliariam escopo e exigiriam política de convite, confirmação e tratamento de credenciais.

### Permissões e duplicidade

- **Decision**: Revalidar no servidor que a pessoa autenticada pode gerenciar o workspace; permitir proprietária e gestoras ativas. Não reativar automaticamente uma associação inativa e não criar uma segunda associação para a proprietária.
- **Rationale**: `Workspace.can_manage_space()` já concentra a regra de gestão e `WorkspaceMembership` já impõe unicidade. O estado inativo representa histórico e não deve ser alterado implicitamente por uma tentativa de inclusão.
- **Alternatives considered**: Exibir apenas a ação para gestoras sem verificar a permissão no POST; reativar uma associação inativa; ambas podem permitir acesso indevido ou mudar estado sem intenção explícita.

### Registro de auditoria

- **Decision**: Criar um evento de auditoria para cada inclusão bem-sucedida e gravá-lo na mesma transação da associação, usando a aplicação `apps.audit` existente.
- **Rationale**: A Constitution exige registro auditável de ações importantes. A aplicação de auditoria atualmente não contém modelo nem implementação, e inclusão de membro altera o acesso a dados do workspace. O evento guarda ator, workspace, conta associada, tipo de ação e instante, sem senha, token ou conteúdo sensível.
- **Alternatives considered**: Não registrar a ação ou usar apenas mensagem ao usuário; nenhuma das opções deixa um registro persistente para auditoria. Criar uma plataforma genérica de auditoria excederia a necessidade desta feature.

### Navegação de retorno

- **Decision**: Apresentar um único controle visual de ícone no layout autenticado compartilhado. Usar histórico somente quando o documento anterior for da mesma origem; definir um destino interno por contexto para acesso direto ou histórico externo.
- **Rationale**: As nove telas autenticadas estendem o template base, permitindo consistência em um único ponto. A verificação de origem impede redirecionamento para fora do produto, e os destinos contextuais garantem que o controle funcione quando uma tela é aberta diretamente.
- **Alternatives considered**: Usar sempre o histórico do navegador, que pode sair do produto ou não ter uma tela anterior útil; repetir um botão com lógica distinta em cada template, o que aumenta duplicação e inconsistência.

### Estilos e acessibilidade dos botões

- **Decision**: Estender os tokens existentes de `auth.css` e aplicar classes semânticas compartilhadas nas telas autenticadas para botões primários, secundários e destrutivos, incluindo hover, foco e desabilitado. Preservar contraste de texto de pelo menos 4,5:1 (3:1 para texto grande).
- **Rationale**: A folha já define uma paleta de floresta, folha e coral e é carregada pelo layout principal. Reutilizá-la evita dependência adicional e permite harmonizar as telas com a identidade existente.
- **Alternatives considered**: Manter utilitários de cor isolados em cada template, que perpetuam divergências; adicionar biblioteca visual, sem necessidade para a escala atual.

## Contexto local confirmado

- `WorkspaceMembership` possui `role`, `is_active` e restrição única para o par workspace/usuário.
- `Workspace.can_manage_space()` permite proprietária ou membro ativo com papel `MANAGER`; views existentes usam autorização no servidor.
- `WorkspaceDetailView` já carrega as associações com os usuários, e o template de detalhe já apresenta a lista de membros.
- `src/templates/base.html` é o layout compartilhado; dashboard, tarefas, workspaces e agendamento têm nove telas autenticadas que o estendem. Login e cadastro são telas públicas.
- `src/static/css/auth.css` contém tokens de cor e estilos do fluxo de autenticação, mas o restante da aplicação usa classes utilitárias diversas.
- `apps.audit` possui configuração e diretório de migrações, mas não está registrada em `INSTALLED_APPS`; seu modelo precisará ser habilitado em `src/setup/settings/base.py`.
- O projeto usa Python 3.12, Django 6.1.2, templates Django, Tailwind carregado no navegador, PostgreSQL, pytest-django e Ruff; não há necessidade de nova dependência.

## Pontos resolvidos

- Não há decisões técnicas pendentes que impeçam o design.
- Uma associação pré-existente, inclusive inativa, não será reativada por este fluxo; a pessoa receberá retorno informativo.
- A aplicação da constituição adiciona um registro de auditoria como suporte interno obrigatório, sem ampliar a experiência ou os casos de uso apresentados ao usuário.