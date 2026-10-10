# Especificação técnica definitiva — Organizador de Tarefas

Versão 1.0 · Documento de referência para desenvolvimento com Python, Django e GitHub Copilot

Este documento consolida as definições funcionais aprovadas e estabelece a arquitetura, os modelos de dados, as regras de autorização, o processamento de recorrências, a segurança e o backlog de implementação.

O objetivo é que cada fase possa ser executada pelo GitHub Copilot de forma controlada, com critérios de aceite e testes, sem gerar a aplicação inteira de uma só vez.

## 1. Escopo funcional aprovado

Calendário semanal e mensal

Visualização de tarefas e ocorrências, com destaque para sábados e domingos.

Espaços compartilhados

Cada espaço possui membros, papéis e regras próprias de autorização.

Conclusão independente

Cada ocorrência possui atribuições e conclusão individual por responsável.

Autenticação dupla

Login por e-mail e senha, além de autenticação social com Google.

Recorrência de fim de semana

Programações semanais, quinzenais e mensais, incluindo todos os sábados e domingos de cada mês.

Notificações

Central de notificações no sistema e envio de e-mails assíncronos.

### Premissas funcionais

1. Um usuário poderá participar de vários espaços compartilhados.
2. Um espaço poderá ter vários membros, com diferentes papéis.
3. Uma programação recorrente definirá a regra; suas ocorrências representarão as tarefas em datas concretas.
4. Cada ocorrência poderá ter um ou mais responsáveis, com estados de conclusão independentes.
5. As tarefas concluídas e seus históricos serão preservados quando a regra de recorrência for alterada.
6. O sistema terá um painel de notificações, com opção de marcar notificações como lidas, além de envio de e-mails.
7. Os recursos serão acessíveis pela interface web responsiva, utilizando Django Templates e Tailwind CSS.

## 2. Arquitetura tecnológica

| Componente             | Decisão                                                                   |
| ---------------------- | ------------------------------------------------------------------------- |
| Linguagem              | Python, versão estável suportada pela versão de Django selecionada        |
| Backend                | Django, com Class-Based Views como padrão                                 |
| Banco                  | PostgreSQL                                                                |
| Interface              | HTML, Tailwind CSS e JavaScript mínimo                                    |
| Autenticação           | Modelo personalizado baseado em `AbstractUser`                            |
| Login social           | Django Allauth com provedor Google                                        |
| Tarefas assíncronas    | Celery Worker                                                             |
| Agendamento de rotinas | Celery Beat                                                               |
| Broker                 | Redis                                                                     |
| Infraestrutura local   | Docker Compose                                                            |
| CI/CD                  | GitHub Actions                                                            |
| Testes                 | pytest, pytest-django e ferramentas complementares                        |
| Qualidade              | Ruff, verificações de segurança de dependências e análise estática        |
| Logs                   | Logging estruturado, identificadores de correlação e eventos de auditoria |

A arquitetura será um monólito modular. Os aplicativos compartilharão o mesmo banco PostgreSQL, mas cada módulo terá responsabilidades e interfaces claras.

Não será necessário introduzir microsserviços, frontend SPA ou uma infraestrutura distribuída na primeira versão.

### Diagrama de componentes

\#chatgpt-mermaid-\_r_qf\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(237, 237, 237);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_qf\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_qf\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_qf\_ .error-icon{fill:rgb(48, 48, 48);}#chatgpt-mermaid-\_r_qf\_ .error-text{fill:rgb(237, 237, 237);stroke:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_qf\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_qf\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_qf\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_qf\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_qf\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_qf\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_qf\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_qf\_ .marker.cross{stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_qf\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_qf\_ p{margin:0;}#chatgpt-mermaid-\_r_qf\_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_qf\_ .cluster-label text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_qf\_ .cluster-label span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_qf\_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-\_r_qf\_ .label text,#chatgpt-mermaid-\_r_qf\_ span{fill:rgb(237, 237, 237);color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_qf\_ .node rect,#chatgpt-mermaid-\_r_qf\_ .node circle,#chatgpt-mermaid-\_r_qf\_ .node ellipse,#chatgpt-mermaid-\_r_qf\_ .node polygon,#chatgpt-mermaid-\_r_qf\_ .node path{fill:rgb(9, 23, 44);stroke:rgb(31, 78, 148);stroke-width:1px;}#chatgpt-mermaid-\_r_qf\_ .rough-node .label text,#chatgpt-mermaid-\_r_qf\_ .node .label text,#chatgpt-mermaid-\_r_qf\_ .image-shape .label,#chatgpt-mermaid-\_r_qf\_ .icon-shape .label{text-anchor:middle;}#chatgpt-mermaid-\_r_qf\_ .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#chatgpt-mermaid-\_r_qf\_ .rough-node .label,#chatgpt-mermaid-\_r_qf\_ .node .label,#chatgpt-mermaid-\_r_qf\_ .image-shape .label,#chatgpt-mermaid-\_r_qf\_ .icon-shape .label{text-align:center;}#chatgpt-mermaid-\_r_qf\_ .node.clickable{cursor:pointer;}#chatgpt-mermaid-\_r_qf\_ .root .anchor path{fill:rgb(175, 175, 175)!important;stroke-width:0;stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_qf\_ .arrowheadPath{fill:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_qf\_ .edgePath .path{stroke:rgb(175, 175, 175);stroke-width:1px;}#chatgpt-mermaid-\_r_qf\_ .flowchart-link{stroke:rgb(175, 175, 175);fill:none;}#chatgpt-mermaid-\_r_qf\_ .edgeLabel{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_qf\_ .edgeLabel p{background-color:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_qf\_ .edgeLabel rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_qf\_ .labelBkg{background-color:rgba(0, 0, 0, 0.5);}#chatgpt-mermaid-\_r_qf\_ .cluster rect{fill:rgb(48, 48, 48);stroke:rgba(255, 255, 255, 0.15);stroke-width:1px;}#chatgpt-mermaid-\_r_qf\_ .cluster text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_qf\_ .cluster span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_qf\_ div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:12px;background:rgb(48, 48, 48);border:1px solid rgba(255, 255, 255, 0.15);border-radius:2px;pointer-events:none;z-index:100;}#chatgpt-mermaid-\_r_qf\_ .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_qf\_ rect.text{fill:none;stroke-width:0;}#chatgpt-mermaid-\_r_qf\_ .icon-shape,#chatgpt-mermaid-\_r_qf\_ .image-shape{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_qf\_ .icon-shape p,#chatgpt-mermaid-\_r_qf\_ .image-shape p{background-color:rgb(0, 0, 0);padding:2px;}#chatgpt-mermaid-\_r_qf\_ .icon-shape .label rect,#chatgpt-mermaid-\_r_qf\_ .image-shape .label rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_qf\_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-\_r_qf\_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-\_r_qf\_ .node .neo-node{stroke:rgb(31, 78, 148);}#chatgpt-mermaid-\_r_qf\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_qf\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_qf\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_qf\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_qf\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_qf\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_qf\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_qf\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_qf\_ [data-look="neo"].node .neo-line path{stroke:rgb(31, 78, 148);filter:none;}#chatgpt-mermaid-\_r_qf\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_qf\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_qf\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_qf\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_qf\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_qf\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_qf\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_qf\_ .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:rgb(153, 206, 255);}#chatgpt-mermaid-\_r_qf\_ .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-0.08px;fill:rgb(153, 206, 255);}#chatgpt-mermaid-\_r_qf\_ .node tspan[font-weight="normal"],#chatgpt-mermaid-\_r_qf\_ .edgeLabels tspan[font-weight="normal"]{font-weight:600;}#chatgpt-mermaid-\_r_qf\_ .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-width:1px;}#chatgpt-mermaid-\_r_qf\_ .node rect,#chatgpt-mermaid-\_r_qf\_ .node circle,#chatgpt-mermaid-\_r_qf\_ .node ellipse,#chatgpt-mermaid-\_r_qf\_ .node polygon,#chatgpt-mermaid-\_r_qf\_ .node path{fill:rgb(0, 40, 77);stroke:rgba(255, 255, 255, 0.1);stroke-width:1px;}#chatgpt-mermaid-\_r_qf\_ .node rect{rx:16px;ry:16px;}#chatgpt-mermaid-\_r_qf\_ .node.mermaid-decision .label-container{fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-dasharray:2,2;}#chatgpt-mermaid-\_r_qf\_ .edgePaths .flowchart-link{stroke:rgb(175, 175, 175);stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}#chatgpt-mermaid-\_r_qf\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_qf\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}Navegador: HTML + TailwindDjango: CBVs e serviçosContas e autorizaçãoEspaços compartilhadosTarefas e atribuiçõesRegras e ocorrênciasNotificaçõesAuditoriaPostgreSQLRedisCelery WorkerCelery BeatProvedor de e-mail

O Redis será utilizado como broker do Celery, não como banco principal dos dados de negócio. As tarefas, atribuições, ocorrências, notificações e registros de auditoria terão persistência no PostgreSQL.

## 3. Estrutura definitiva de pastas

```
organizador-tarefas/
├── .github/
│   ├── copilot-instructions.md
│   └── workflows/
│       ├── ci.yml
│       └── security.yml
├── .env
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── README.md
├── docs/
│   ├── architecture.md
│   ├── authorization.md
│   ├── recurrence-rules.md
│   ├── security.md
│   └── deployment.md
├── scripts/
├── media/
└── src/
    ├── manage.py
    ├── setup/
    │   ├── __init__.py
    │   ├── urls.py
    │   ├── asgi.py
    │   ├── wsgi.py
    │   ├── celery.py
    │   └── settings/
    │       ├── __init__.py
    │       ├── base.py
    │       ├── local.py
    │       └── prod.py
    ├── apps/
    │   ├── accounts/
    │   ├── access/
    │   ├── workspaces/
    │   ├── tasks/
    │   ├── scheduling/
    │   ├── notifications/
    │   ├── audit/
    │   └── dashboard/
    ├── templates/
    └── static/
```

A estrutura representa a organização desejada, não arquivos que já foram criados.

### Regras estruturais

- `base.py` conterá configurações comuns; `local.py` e `prod.py` aplicarão configurações específicas de cada ambiente.
- O ambiente será selecionado por variável, como `DJANGO_SETTINGS_MODULE`.
- O `.env` real ficará fora do versionamento. `.env.example` conterá apenas nomes e valores ilustrativos não secretos.
- `media/` será um volume persistente, não incorporado à imagem Docker.
- Cada app terá modelos, URLs, views, testes e migrações próprios.
- As configurações de produção não poderão herdar acidentalmente valores inseguros de desenvolvimento.
- Dependências, versões e comandos de execução serão documentados no `pyproject.toml` e no README.

## 4. Modelo de usuários e autenticação

### 4.1 Usuário personalizado

O modelo de usuário deverá ser definido antes da primeira migração do banco. Não criaremos um modelo independente que duplique a autenticação do Django; utilizaremos `AbstractUser`, ampliando-o com os campos necessários.

```
# src/apps/accounts/models.pyfrom django.contrib.auth.models import AbstractUserfrom django.db import modelsclass User(AbstractUser):    email = models.EmailField(unique=True)    display_name = models.CharField(max_length=150, blank=True)    timezone = models.CharField(        max_length=64,        default="America/Sao_Paulo",    )    class Meta:        db_table = "accounts_user"    def __str__(self):        return self.display_name or self.username
```

Configuração em `src/setup/settings/base.py`:

```
AUTH_USER_MODEL = "accounts.User"
```

Decisões adicionais:

- O identificador principal será o ID interno do banco, preferencialmente UUID para entidades compartilháveis externamente.
- O login inicial usará username ou e-mail conforme a configuração final do backend de autenticação.
- O e-mail será único e terá validação de verificação.
- Senhas serão tratadas pelos mecanismos nativos do Django.
- O usuário terá preferências de fuso horário e notificações.
- Não utilizaremos o e-mail como chave estrangeira para relacionamentos de negócio.

O exemplo mantém o campo `username` do `AbstractUser`. Se o requisito futuro for autenticação exclusivamente por e-mail, essa mudança deve ser planejada antes da migração inicial, definindo `USERNAME_FIELD` e o manager correspondente.

### 4.2 Login Google

O fluxo de autenticação social usará Django Allauth, com o provedor Google configurado no ambiente.

Requisitos:

- Login tradicional e Google disponíveis na mesma tela.
- Verificação do e-mail conforme a política definida.
- Fluxo seguro de associação de contas.
- Proteção contra tentativas de vinculação indevida.
- Segredos OAuth exclusivamente em variáveis de ambiente.
- URLs de callback registradas e restritas aos domínios autorizados.
- Testes de login, logout, falhas do provedor e contas duplicadas.

O login Google identifica o usuário; ele não concede automaticamente papel de administrador ou acesso a espaços compartilhados.

## 5. Autorização: perfis globais e papéis por espaço

A autorização será dividida em duas dimensões independentes.

Perfil global: determina as funcionalidades administrativas disponíveis para o usuário no sistema.

Papel no espaço: determina o que o usuário pode fazer dentro de um espaço específico.

O Django Groups e seu sistema de permissões podem atender à autorização global. A participação em espaços e seus papéis será modelada separadamente.

### 5.1 Modelos de acesso

`AccessProfile` poderá ser utilizado para associar um perfil funcional ao usuário, se o projeto realmente precisar de perfis nomeados como administrador, suporte e usuário padrão. As permissões granulares do Django continuam sendo a fonte de autorização global.

```
# src/apps/access/models.pyfrom django.conf import settingsfrom django.db import modelsclass AccessProfile(models.Model):    name = models.CharField(max_length=80, unique=True)    users = models.ManyToManyField(        settings.AUTH_USER_MODEL,        related_name="access_profiles",        blank=True,    )    def __str__(self):        return self.name
```

Esse modelo representa uma associação de usuários a perfis. As permissões efetivas deverão ser atribuídas por grupos e permissões do Django ou por um mapeamento explícito e testado, nunca inferidas apenas pelo nome do perfil.

### 5.2 Espaços compartilhados

O espaço será a unidade principal de colaboração. As tarefas, programações e ocorrências pertencerão a um espaço.

```
# src/apps/workspaces/models.pyimport uuidfrom django.conf import settingsfrom django.db import modelsclass Workspace(models.Model):    id = models.UUIDField(        primary_key=True,        default=uuid.uuid4,        editable=False,    )    name = models.CharField(max_length=150)    description = models.TextField(blank=True)    owner = models.ForeignKey(        settings.AUTH_USER_MODEL,        on_delete=models.PROTECT,        related_name="owned_workspaces",    )    created_at = models.DateTimeField(auto_now_add=True)    updated_at = models.DateTimeField(auto_now=True)    is_active = models.BooleanField(default=True)    def __str__(self):        return self.nameclass WorkspaceMembership(models.Model):    class Role(models.TextChoices):        MANAGER = "manager", "Gestor"        COLLABORATOR = "collaborator", "Colaborador"        READER = "reader", "Leitor"    workspace = models.ForeignKey(        Workspace,        on_delete=models.PROTECT,        related_name="memberships",    )    user = models.ForeignKey(        settings.AUTH_USER_MODEL,        on_delete=models.PROTECT,        related_name="workspace_memberships",    )    role = models.CharField(        max_length=20,        choices=Role.choices,    )    joined_at = models.DateTimeField(auto_now_add=True)    is_active = models.BooleanField(default=True)    class Meta:        constraints = [            models.UniqueConstraint(                fields=["workspace", "user"],                name="unique_workspace_user",            )        ]
```

A associação deverá ser criada inicialmente pelo proprietário ou por um gestor autorizado. Um usuário não poderá se adicionar a um espaço arbitrário alterando parâmetros de uma requisição.

Os convites serão um recurso separado, com token aleatório, validade, estado, destinatário opcional e registro de quem convidou. O token deve ser armazenado de forma segura, possuir prazo de expiração e ser invalidado após o uso.

### 5.3 Matriz de autorização definitiva

A matriz abaixo define o comportamento esperado para a primeira versão.

| Operação                           | Administrador global                | Gestor                      | Colaborador                        | Leitor |
| ---------------------------------- | ----------------------------------- | --------------------------- | ---------------------------------- | ------ |
| Criar espaço                       | Sim                                 | Sim                         | Não                                | Não    |
| Editar configurações do espaço     | Sim                                 | Sim                         | Não                                | Não    |
| Gerenciar membros e convites       | Sim                                 | Sim                         | Não                                | Não    |
| Criar tarefas e programações       | Sim                                 | Sim                         | Sim                                | Não    |
| Editar tarefa compartilhada        | Sim                                 | Sim                         | Conforme atribuição ou autorização | Não    |
| Atribuir responsáveis              | Sim                                 | Sim                         | Conforme permissão                 | Não    |
| Consultar calendário               | Sim                                 | Sim                         | Sim                                | Sim    |
| Atualizar sua própria conclusão    | Sim                                 | Sim                         | Sim, se atribuído                  | Não    |
| Alterar conclusão de outro usuário | Sim, com autorização administrativa | Conforme política do espaço | Não                                | Não    |
| Encerrar espaço                    | Sim                                 | Sim                         | Não                                | Não    |

O administrador global não deve receber acesso irrestrito aos dados pessoais de todos os espaços por simples conveniência. O acesso administrativo a dados de negócio deve ser justificado, autorizado e auditável.

Regra de implementação: toda consulta de objetos compartilhados deve ser filtrada pelo espaço e pela participação ativa do usuário. Não basta buscar um objeto por ID e depois verificar apenas se o usuário está autenticado.

As CBVs deverão usar mixins de login, permissões e filtragem de querysets. Para regras complexas, a autorização será centralizada em funções ou services reutilizáveis.

## 6. Modelagem das tarefas e das atribuições

É necessário distinguir três entidades:

- Task: definição da tarefa e suas informações gerais.
- ScheduleRule: regra de recorrência responsável por determinar as datas.
- TaskOccurrence: execução concreta da tarefa em uma data.

A conclusão pertence à atribuição individual, pois o requisito é permitir que cada responsável conclua sua parte de forma independente.

### 6.1 Tarefa

```
# src/apps/tasks/models.pyimport uuidfrom django.conf import settingsfrom django.db import modelsclass Task(models.Model):    class Status(models.TextChoices):        ACTIVE = "active", "Ativa"        ARCHIVED = "archived", "Arquivada"    id = models.UUIDField(        primary_key=True,        default=uuid.uuid4,        editable=False,    )    workspace = models.ForeignKey(        "workspaces.Workspace",        on_delete=models.PROTECT,        related_name="tasks",    )    title = models.CharField(max_length=200)    description = models.TextField(blank=True)    created_by = models.ForeignKey(        settings.AUTH_USER_MODEL,        on_delete=models.PROTECT,        related_name="created_tasks",    )    status = models.CharField(        max_length=20,        choices=Status.choices,        default=Status.ACTIVE,    )    created_at = models.DateTimeField(auto_now_add=True)    updated_at = models.DateTimeField(auto_now=True)    def __str__(self):        return self.title
```

A tarefa representa a definição reutilizável. Sua arquivação impedirá novas ocorrências, mas não apagará automaticamente o histórico existente.

### 6.2 Ocorrência

```
# src/apps/scheduling/models.pyimport uuidfrom django.db import modelsclass TaskOccurrence(models.Model):    class Status(models.TextChoices):        OPEN = "open", "Aberta"        CANCELLED = "cancelled", "Cancelada"    id = models.UUIDField(        primary_key=True,        default=uuid.uuid4,        editable=False,    )    task = models.ForeignKey(        "tasks.Task",        on_delete=models.PROTECT,        related_name="occurrences",    )    schedule_rule = models.ForeignKey(        "scheduling.ScheduleRule",        on_delete=models.PROTECT,        related_name="occurrences",    )    scheduled_date = models.DateField()    starts_at = models.TimeField(null=True, blank=True)    due_at = models.DateTimeField(null=True, blank=True)    status = models.CharField(        max_length=20,        choices=Status.choices,        default=Status.OPEN,    )    created_at = models.DateTimeField(auto_now_add=True)
```

A restrição de unicidade é essencial para que duas execuções do Celery não criem a mesma ocorrência. Antes da implementação, também deve ser definida a estratégia para tarefas avulsas que não possuam regra de recorrência; nesse caso, o relacionamento com `ScheduleRule` precisará ser opcional, com uma política de unicidade própria.

### 6.3 Atribuição e conclusão individual

```
# src/apps/tasks/models.pyfrom django.conf import settingsfrom django.db import modelsclass TaskAssignment(models.Model):    class Status(models.TextChoices):        PENDING = "pending", "Pendente"        COMPLETED = "completed", "Concluída"        CANCELLED = "cancelled", "Cancelada"    occurrence = models.ForeignKey(        "scheduling.TaskOccurrence",        on_delete=models.PROTECT,        related_name="assignments",    )    user = models.ForeignKey(        settings.AUTH_USER_MODEL,        on_delete=models.PROTECT,        related_name="task_assignments",    )    status = models.CharField(        max_length=20,        choices=Status.choices,        default=Status.PENDING,    )    completed_at = models.DateTimeField(null=True, blank=True)    completed_by = models.ForeignKey(        settings.AUTH_USER_MODEL,        null=True,        blank=True,        on_delete=models.PROTECT,        related_name="completed_task_assignments",    )    created_at = models.DateTimeField(auto_now_add=True)    class Meta:        constraints = [            models.UniqueConstraint(                fields=["occurrence", "user"],                name="unique_occurrence_user",            )        ]
```

O modelo deve ser completado com validações para manter `completed_at` e `completed_by` consistentes com o estado. Essas validações devem estar no serviço de domínio e, quando possível, protegidas também por restrições de banco.

Exemplo de comportamento:

- João e Maria são atribuídos à ocorrência de sábado.
- João conclui sua atribuição; o status dele passa para `COMPLETED`.
- Maria continua com status `PENDING`.
- A ocorrência não será considerada integralmente concluída enquanto houver atribuições obrigatórias pendentes.
- Se não houver responsáveis, a política de conclusão deverá ser explícita para evitar ocorrências eternamente pendentes.

A alteração do estado de uma atribuição será executada em uma transação, verificando novamente a autorização do usuário e registrando o evento de auditoria.

## 7. Modelagem da recorrência

A recorrência precisa ser suficientemente flexível para representar três regras distintas: semanal, quinzenal e mensal. Não devemos implementar cada regra com tarefas Celery específicas; a geração de datas deve ficar em um serviço de domínio testável.

### 7.1 Modelo `ScheduleRule`

```
# src/apps/scheduling/models.pyfrom django.conf import settingsfrom django.db import modelsclass ScheduleRule(models.Model):    class Frequency(models.TextChoices):        WEEKLY = "weekly", "Semanal"        BIWEEKLY = "biweekly", "Quinzenal"        MONTHLY = "monthly", "Mensal"    task = models.ForeignKey(        "tasks.Task",        on_delete=models.PROTECT,        related_name="schedule_rules",    )    frequency = models.CharField(        max_length=20,        choices=Frequency.choices,    )    starts_on = models.DateField()    ends_on = models.DateField(null=True, blank=True)    # Dias ISO: segunda=1, ..., sábado=6, domingo=7.    weekdays = models.JSONField(default=list)    timezone = models.CharField(        max_length=64,        default="America/Sao_Paulo",    )    is_active = models.BooleanField(default=True)    created_by = models.ForeignKey(        settings.AUTH_USER_MODEL,        on_delete=models.PROTECT,        related_name="created_schedule_rules",
```

Esse modelo é um ponto de partida. A validação dos dias, das frequências e das datas será implementada em um serviço específico. A regra mensal deverá possuir um modo de seleção que permita distinguir “todos os sábados e domingos” de outras regras mensais futuras.

### 7.2 Regras de geração

| Tipo        | Regra                                                                             |
| ----------- | --------------------------------------------------------------------------------- |
| Semanal     | Repetir nas semanas correspondentes, nos dias ISO selecionados                    |
| Quinzenal   | Repetir a cada 14 dias, respeitando uma data de referência e os dias selecionados |
| Mensal      | Gerar ocorrências em todos os sábados e domingos de cada mês                      |
| Início      | Nunca gerar ocorrências anteriores a `starts_on`                                  |
| Término     | Não gerar ocorrências posteriores a `ends_on`, se definido                        |
| Pausa       | Não gerar novas ocorrências enquanto a regra estiver inativa                      |
| Duplicidade | Uma mesma regra não poderá gerar duas ocorrências para a mesma data               |

Para a recorrência quinzenal, a data de referência precisa ser armazenada de forma explícita, pois apenas os dias da semana não determinam quais semanas são válidas. Uma extensão recomendada é acrescentar `anchor_date` ao modelo, usada como referência para calcular os intervalos de 14 dias.

Para a regra mensal, o gerador deverá percorrer as datas do mês e selecionar os sábados e domingos. Não deve assumir que cada mês possui quatro fins de semana ou que o último domingo pertence sempre à quarta semana.

### 7.3 Serviço de geração

O serviço ficará em `src/apps/scheduling/services.py` e deverá:

1. Receber a regra e um intervalo de datas.
2. Validar o estado e os limites da regra.
3. Calcular as datas elegíveis.
4. Excluir datas com exceções ou cancelamentos aplicáveis.
5. Criar as ocorrências com `get_or_create()` ou estratégia equivalente.
6. Criar atribuições iniciais conforme a política de responsáveis.
7. Registrar o resultado do processamento.
8. Retornar métricas de ocorrências criadas, já existentes e ignoradas.

A operação deverá ser idempotente e segura diante de concorrência. `get_or_create()` não substitui a restrição de unicidade do banco.

### 7.4 Política para alterações e exceções

As seguintes regras são obrigatórias:

- Uma alteração na programação não deve reescrever ocorrências concluídas.
- Ocorrências futuras sem execução poderão ser atualizadas conforme a política definida.
- Uma ocorrência cancelada deve permanecer no histórico.
- Mudanças de responsáveis não devem apagar atribuições concluídas.
- A regeneração não poderá restaurar silenciosamente ocorrências canceladas.
- Falhas no processamento devem ser registradas e passíveis de nova tentativa.

O sistema deverá definir se uma edição de programação afeta imediatamente todas as ocorrências futuras ou somente as criadas após a alteração. A recomendação é aplicar a mudança às ocorrências futuras ainda abertas, preservando exceções explícitas e o histórico concluído.

## 8. Notificações no sistema e por e-mail

O módulo `notifications` será responsável por persistir notificações e solicitar o envio de e-mails.

### Modelo inicial

```
# src/apps/notifications/models.pyfrom django.conf import settingsfrom django.db import modelsclass Notification(models.Model):    user = models.ForeignKey(        settings.AUTH_USER_MODEL,        on_delete=models.PROTECT,        related_name="notifications",    )    event_type = models.CharField(max_length=80)    title = models.CharField(max_length=180)    message = models.TextField()    target_url = models.CharField(max_length=500, blank=True)    created_at = models.DateTimeField(auto_now_add=True)    read_at = models.DateTimeField(null=True, blank=True)    class Meta:        indexes = [            models.Index(                fields=["user", "read_at", "created_at"],                name="notification_user_read_idx",            )        ]
```

Para o envio de e-mails, será necessário um modelo complementar, como `EmailDelivery`, que registre o destinatário, a categoria da mensagem, o estado do envio, o número de tentativas, a data do último erro e o identificador do provedor quando disponível. O conteúdo deverá evitar a exposição de dados privados desnecessários.

### Eventos que geram notificações

- Convite para um espaço.
- Inclusão ou remoção de um membro.
- Atribuição de uma ocorrência.
- Alteração de prazo ou responsável.
- Lembrete de tarefa próxima do vencimento.
- Tarefa atrasada.
- Conclusão de uma atribuição.
- Falha relevante no processamento de uma programação, destinada ao usuário responsável pela administração.

### Fluxo de envio

1. A operação de negócio é validada e salva no PostgreSQL.
2. A solicitação de notificação é registrada de maneira confiável.
3. Uma tarefa Celery processa o envio.
4. O resultado é persistido.
5. Em caso de falha temporária, a tarefa pode ser repetida com backoff.
6. Após o limite de tentativas, o evento é encaminhado para tratamento operacional.

O sistema deverá impedir e-mails duplicados quando uma mesma operação gerar eventos repetidos. Para notificações críticas, o padrão transactional outbox é preferível: a intenção de envio é registrada na mesma transação do evento de negócio, e um worker a publica posteriormente.

As preferências de cada usuário deverão permitir habilitar ou desabilitar categorias de e-mail, respeitando mensagens operacionais essenciais e as obrigações aplicáveis.

## 9. Auditoria, logs e rastreabilidade

O módulo `audit` terá a função de registrar ações relevantes de negócio e administração.

### 9.1 Modelo de auditoria

```
# src/apps/audit/models.pyimport uuidfrom django.conf import settingsfrom django.db import modelsclass AuditEvent(models.Model):    id = models.UUIDField(        primary_key=True,        default=uuid.uuid4,        editable=False,    )    actor = models.ForeignKey(        settings.AUTH_USER_MODEL,        null=True,        blank=True,        on_delete=models.PROTECT,        related_name="audit_events",    )    action = models.CharField(max_length=100)    entity_type = models.CharField(max_length=100)    entity_id = models.CharField(max_length=100)    workspace_id = models.UUIDField(null=True, blank=True)    correlation_id = models.UUIDField(null=True, blank=True)    occurred_at = models.DateTimeField(auto_now_add=True)    metadata = models.JSONField(default=dict)
```

O modelo é ilustrativo e precisará de uma política para eventos de sistema sem usuário associado. A coluna `workspace_id` poderá ser um identificador de contexto sem relacionamento direto, evitando acoplamento desnecessário; quando a integridade referencial for essencial, será avaliado um relacionamento formal.

### 9.2 Eventos obrigatórios

- Login bem-sucedido e tentativas relevantes de login malsucedido.
- Alterações de perfil e permissões.
- Criação, revogação e aceitação de convites.
- Inclusão e remoção de membros.
- Criação e edição de programações.
- Cancelamento de ocorrências.
- Mudanças de atribuição e conclusão.
- Operações administrativas sobre contas e espaços.
- Tentativas de acesso negado relevantes.
- Reprocessamento administrativo de tarefas assíncronas.

Os eventos de auditoria deverão ser registrados por serviços de domínio, não exclusivamente por sinais Django. Sinais podem complementar a solução, mas não devem ser o único mecanismo de auditoria das operações críticas.

### 9.3 Integridade dos registros

Os registros devem ser acessíveis somente a usuários autorizados, sem edição ou exclusão pela interface comum. Em produção, a política deverá incluir retenção, backup, monitoramento e, conforme o risco, envio para armazenamento externo com controles de integridade.

Logs operacionais e auditoria não são a mesma coisa: logs ajudam a diagnosticar falhas; auditoria documenta quem fez o quê, quando e sobre qual entidade.

## 10. Configuração de infraestrutura e execução

O Docker Compose deverá definir pelo menos:

- `django-app`: aplicação web Django.
- `postgres`: banco de dados.
- `redis`: broker.
- `celery-worker`: execução de tarefas.
- `celery-beat`: agendamento periódico.

Um proxy reverso com TLS será necessário na infraestrutura de produção, embora possa ser gerenciado separadamente do Compose de desenvolvimento.

### Responsabilidades por serviço

| Serviço         | Responsabilidade                                                      |
| --------------- | --------------------------------------------------------------------- |
| `django-app`    | Receber requisições, autenticar, autorizar e executar operações web   |
| `postgres`      | Persistir os dados de negócio                                         |
| `redis`         | Transportar mensagens para o Celery                                   |
| `celery-worker` | Gerar ocorrências, enviar notificações e executar rotinas assíncronas |
| `celery-beat`   | Disparar rotinas periódicas                                           |
| Proxy reverso   | Terminar HTTPS, encaminhar tráfego e aplicar limites básicos          |

### Requisitos operacionais

- Health checks para serviços essenciais.
- Dependências com condições de disponibilidade quando suportadas pelo Compose.
- Volumes persistentes para PostgreSQL e mídias.
- Redes internas para banco e Redis.
- Nenhuma porta de banco ou Redis publicada desnecessariamente.
- Processo de migração executado de forma controlada no deploy.
- Usuário de sistema sem privilégios administrativos desnecessários no container.
- Configurações e segredos distintos entre desenvolvimento e produção.
- Reinicialização adequada de workers e política de encerramento gracioso.

O Celery Beat deverá possuir apenas uma instância ativa por agenda para evitar disparos duplicados. Mesmo assim, as tarefas de negócio deverão ser idempotentes, porque mensagens podem ser repetidas.

## 11. Segurança para produção

A implementação será avaliada por controles de segurança em cada fase.

Autenticação

Hash de senhas seguro, proteção contra abuso no login, recuperação de senha e fluxo OAuth validado.

Autorização

Verificação de pertencimento ao espaço em toda leitura ou alteração de dados compartilhados.

Web

CSRF, escaping de templates, validação de entrada, cookies seguros e HTTPS.

Uploads

Limites de tamanho, validação do conteúdo, nomes seguros e acesso autorizado.

Segredos

Nenhuma chave ou senha em código, imagens Docker, logs ou repositório.

Dependências

Versões controladas, atualizações e análise automatizada de vulnerabilidades.

Dados

Privilégios mínimos, backups, restauração testada e retenção definida.

Monitoramento

Logs estruturados, alertas de falhas, correlação de requisições e rastreabilidade das rotinas.

Também deverão ser configurados `SECURE_SSL_REDIRECT`, cookies `Secure`, política HSTS após validar a infraestrutura HTTPS, `CSRF_TRUSTED_ORIGINS` restrito, `ALLOWED_HOSTS` explícito e o comando `manage.py check --deploy`.

Não será permitido confiar em IDs enviados pelo navegador para definir o espaço de destino ou o usuário responsável. Esses valores deverão ser validados contra o contexto autenticado e as permissões vigentes.

## 12. Estratégia de testes e critérios de qualidade

A implementação deverá usar testes automatizados desde a primeira fase.

| Tipo de teste | O que validar                                                 |
| ------------- | ------------------------------------------------------------- |
| Unitários     | Cálculo de datas, validação de regras e transições de estado  |
| Modelos       | Restrições de unicidade, integridade e relacionamentos        |
| Views         | Respostas HTTP, formulários, redirects e filtros              |
| Autorização   | Acesso permitido e negado por perfil e espaço                 |
| Integração    | Fluxos completos entre tarefa, ocorrência e atribuição        |
| Celery        | Retries, idempotência e recuperação de falhas                 |
| Autenticação  | Login tradicional, Google e recuperação de senha              |
| Segurança     | Acesso cruzado entre espaços, CSRF e uploads                  |
| Operacionais  | Migrações, inicialização dos serviços e restauração de backup |

### Casos de teste obrigatórios para recorrência

- Sábado e domingo em meses de 28, 29, 30 e 31 dias.
- Fim de ano e mudança de ano.
- Ano bissexto.
- Regra iniciada no meio de uma semana ou mês.
- Regra com data final.
- Programação quinzenal ancorada em datas diferentes.
- Duas execuções concorrentes do gerador.
- Reprocessamento de uma regra já executada.
- Ocorrência concluída ou cancelada antes da alteração da regra.
- Mudança de fuso horário e tarefas com horários próximos à meia-noite.

### Critérios de aceite globais

A versão não poderá ser considerada pronta para produção enquanto:

1. Usuários não conseguirem acessar dados de espaços sem autorização.
2. A geração de ocorrências não for idempotente.
3. As conclusões individuais puderem ser sobrescritas indevidamente.
4. Os testes de migração e de autorização não estiverem passando.
5. Segredos de produção estiverem presentes no repositório.
6. Backups não tiverem sido restaurados com sucesso em um teste.
7. Logs e auditoria não estiverem operacionais para os eventos definidos.

## 13. Backlog de implementação por fases

O backlog abaixo organiza o trabalho em entregas incrementais. As estimativas são indicativas para planejamento, não compromissos de prazo.

### Fase 1 — Fundação do projeto (3–5 dias)

Definir versões compatíveis de Python, Django e dependências; criar a estrutura e configurações base/local/prod; preparar Docker Compose com Django, PostgreSQL, Redis, Celery Worker e Beat; criar o modelo User personalizado antes da primeira migração; configurar pytest, Ruff, GitHub Actions e instruções do Copilot; documentar inicialização, migrações e variáveis de ambiente.

**Critério de aceite:** ambiente reproduzível, migrações funcionais e CI executando testes.

### Fase 2 — Identidade e acesso (3–5 dias)

Implementar autenticação tradicional, login social, verificação de e-mail e permissões de identidade/acesso, com testes para fluxos permitidos e negados.

### Fase 3 — Tarefas e colaboração (4–6 dias)

Implementar espaços compartilhados, membros, papéis por espaço, tarefas e atribuições individuais, com autorização e isolamento entre espaços.

### Fase 4 — Recorrências e calendário (5–8 dias)

Implementar regras de recorrência, geração idempotente de ocorrências e visualizações semanal e mensal.

### Fase 5 — Notificações e auditoria (4–6 dias)

Implementar notificações persistentes, entrega assíncrona de e-mails e eventos de auditoria.

### Fase 6 — Produção e homologação (4–7 dias)

Completar controles operacionais e de segurança, validar deploy, monitoramento, backup e restauração.

Estimativa global indicativa: aproximadamente 23 a 37 dias úteis de desenvolvimento. O prazo real dependerá da experiência da equipe, das revisões e dos requisitos adicionais descobertos durante os testes.

### Estado da implementação (10/10/2026)

**Fase 1 — Fundação: concluída no código.** O projeto usa Django 6.1.2, settings separados para base/local/prod, SQLite fixo no ambiente local e PostgreSQL na configuração de produção. O modelo customizado `accounts.User` possui migração inicial. Docker Compose, Celery, CI, pytest, Ruff, logging e documentação inicial estão preparados. A execução dos serviços Docker não foi validada neste ambiente porque Docker não estava disponível.

**Fase 2 — Identidade e acesso: parcialmente implementada.** Django Allauth está configurado para cadastro, login por e-mail e senha, redefinição de senha e verificação obrigatória de e-mail. O provedor Google, suas variáveis de ambiente e as rotas estão preparados; o fluxo OAuth real depende de credenciais Google e ainda não foi homologado. As telas responsivas de login e cadastro foram criadas em Django Templates com Tailwind via CDN e CSS próprio. A gestão explícita de permissões globais e os respectivos testes de autorização ainda estão pendentes.

**Verificações mais recentes:** 5 testes passaram; Ruff e `manage.py check` passaram; `makemigrations --check --dry-run` não encontrou alterações pendentes. O pytest emite um aviso de descontinuação para `EMAIL_BACKEND`, sem falha nos testes.

As Fases 3 a 6 ainda não foram iniciadas. Espaços, membros, papéis por espaço, tarefas, recorrências, calendário, notificações e auditoria permanecem fora da implementação atual.

## 14. Ordem de execução com o GitHub Copilot

A sequência recomendada para cada entrega será:

1. Especificar: solicitar apenas a funcionalidade da fase atual.
2. Planejar: pedir os arquivos afetados, os modelos e os testes necessários.
3. Implementar: desenvolver um módulo ou conjunto pequeno de funcionalidades.
4. Validar: executar testes, lint e verificações de segurança.
5. Revisar: conferir migrações, permissões, transações e logs.
6. Registrar: atualizar documentação e backlog.
7. Integrar: somente depois de passar pelos critérios de aceite, incorporar à branch principal.

Não se deve pedir ao Copilot para implementar todo o sistema em um único comando. A geração incremental facilita a revisão e evita que inconsistências de arquitetura se propaguem.

### Primeiro prompt de implementação

# Tarefa 01 — Fundação do Organizador de Tarefas

Considere a especificação técnica do projeto Organizador de Tarefas como fonte de verdade.

Implemente somente a Fase 1 — Fundação do projeto.

## Objetivos

1. Criar a estrutura de pastas definida na especificação.
2. Configurar Django com settings/base.py, settings/local.py e settings/prod.py.
3. Configurar Docker Compose com django-app, PostgreSQL, Redis, Celery Worker e Celery Beat.
4. Criar o modelo personalizado User baseado em AbstractUser e configurar AUTH_USER_MODEL antes da primeira migração.
5. Configurar pytest, pytest-django, Ruff e GitHub Actions.
6. Criar .env.example, .gitignore, .dockerignore e README.md.
7. Preparar logging estruturado básico.
8. Criar testes iniciais e validar o processo de migração.

## Restrições

- Não implementar ainda os módulos de tarefas, espaços compartilhados, recorrência ou notificações.
- Não utilizar o modelo concreto django.contrib.auth.models.User em relações de negócio.
- Não colocar segredos no repositório.
- Não expor PostgreSQL ou Redis publicamente por padrão.
- Não configurar produção com DEBUG=True.
- Não criar arquivos sem finalidade concreta.
- Fixar e documentar versões compatíveis das dependências.

## Processo obrigatório

1. Apresente primeiro o plano dos arquivos a criar.
2. Implemente somente o escopo solicitado.
3. Execute os testes e as verificações disponíveis.
4. Informe os arquivos alterados, os comandos executados e seus resultados.
5. Relate problemas, limitações e pendências.
6. Não declare testes aprovados sem executá-los.
7. Não avance para a Fase 2 sem autorização.

## Critério de conclusão

O ambiente deve iniciar de forma reproduzível, conectar-se ao PostgreSQL, executar as migrações iniciais, disponibilizar a aplicação Django e passar pelos testes e verificações de qualidade configurados.

## 15. Checklist de governança do projeto

### Acompanhamento de preparação

5 de 9

- [x] Especificação técnica versionada no Git
- [x] Instruções do GitHub Copilot adicionadas
- [x] Modelo User definido antes das migrações
- [ ] Ambiente Docker reproduzível validado em execução
- [x] Permissões e papéis documentados
- [ ] Regras de recorrência cobertas por testes
- [ ] Notificações e auditoria com persistência
- [x] CI configurada para testes e análise estática
- [ ] Backups e restauração testados

Homologação aprovada antes da produção

&#x20;Copiar checklist

Este checklist serve para acompanhar o planejamento e não representa uma verificação automática do repositório.

## 16. Decisões técnicas ainda necessárias antes da produção

A especificação funcional está definida, mas há algumas decisões operacionais que devem ser registradas antes do deploy:

- Provedor de e-mail: SMTP ou serviço transacional, com credenciais protegidas.
- Política de exclusão: retenção de contas, espaços e tarefas históricas.
- Prazo de retenção de auditoria: definido conforme necessidade operacional e obrigações legais.
- Anexos: tipos e limites permitidos, política de acesso e capacidade de armazenamento.
- Lembretes: antecedência, horário de envio e fuso horário.
- Escala de processamento: volume esperado de usuários, tarefas e ocorrências para dimensionar workers e banco.
- Política de exceções: como tratar feriados, pausas, mudanças de responsáveis e ocorrências canceladas.

Essas decisões não impedem o início da Fase 1, mas deverão ser resolvidas antes de implementar os módulos afetados.

