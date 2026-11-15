# Organizador

**Organização de atividades, planejamento de rotinas, colaboração, execução e acompanhamento em um só lugar.**

O Organizador é uma aplicação web para estruturar atividades individuais e compartilhadas, planejar rotinas recorrentes, distribuir responsabilidades e acompanhar a execução do trabalho.

A proposta vai além de uma simples lista de tarefas: o sistema organiza atividades em espaços de trabalho, permite programar ocorrências, registrar execuções e acompanhar o progresso dos participantes.

## Funcionalidades e estado de implementação

O projeto está em desenvolvimento incremental. Esta seção diferencia o que já possui implementação no código, o que está parcialmente disponível e o que permanece planejado. A existência de código não significa, por si só, homologação completa para produção.

| Área | Estado | Observações |
|---|---|---|
| Fundação e infraestrutura | Implementada no código | Configurações Django, modelo de usuário, migrações, CI, testes e ferramentas de qualidade preparados. A execução completa do Docker ainda precisa ser validada. |
| Identidade e autenticação | Parcialmente implementada | Autenticação por e-mail e senha, cadastro e redefinição de senha configurados. O login Google depende de credenciais e homologação OAuth. |
| Espaços e colaboração | Parcialmente implementada | Espaços, membros, papéis e gerenciamento de membros possuem implementação. A cobertura completa de autorização das operações de negócio ainda está em evolução. |
| Atividades e atribuições | Parcialmente implementadas | Criação de tarefas e atribuição de responsáveis às ocorrências implementadas. |
| Recorrências e calendário | Parcialmente implementados | Regras semanais, quinzenais e mensais, geração de ocorrências e calendário mensal implementados. A cobertura completa dos critérios de aceite ainda precisa ser validada. |
| Execução de atividades | Parcialmente implementada | Registro de execução com horários, comentários e anexos possui implementação; a validação funcional e operacional continua. |
| Auditoria | Parcialmente implementada | Eventos relacionados ao gerenciamento de membros foram implementados. A cobertura dos demais eventos previstos permanece pendente. |
| Notificações | Planejada | Central de notificações e envio assíncrono de e-mails ainda precisam ser implementados. |
| Produção e homologação | Pendente | Controles operacionais, segurança, deploy, monitoramento e restauração de backups precisam ser validados. |

## Tecnologias

- Python 3.12
- Django 6.1.2
- PostgreSQL
- SQLite para desenvolvimento local
- Django Templates, HTML, Tailwind CSS e JavaScript mínimo
- Django Allauth para autenticação e login social
- Celery Worker e Celery Beat
- Redis como broker do Celery
- Docker Compose
- pytest e pytest-django
- Ruff
- GitHub Actions

A arquitetura utiliza um monólito modular Django, com separação de responsabilidades por aplicações. O PostgreSQL é o banco principal previsto para produção; o Redis transporta mensagens para o Celery e não é utilizado como banco dos dados de negócio.

## Estrutura do projeto

A aplicação está organizada por módulos, com responsabilidades separadas:

- `accounts`: identidade e autenticação.
- `access`: permissões e controle de acesso.
- `workspaces`: espaços de trabalho, membros e papéis.
- `tasks`: atividades e atribuições.
- `scheduling`: regras de recorrência, ocorrências e calendário.
- `notifications`: notificações.
- `audit`: registros de auditoria.
- `dashboard`: visão geral e acompanhamento.

A estrutura detalhada e as responsabilidades de cada módulo estão documentadas em `spec.md`.

## Requisitos locais

- Python 3.12
- pip
- Docker + Docker Compose (opcional para execução dos serviços)

## Inicialização rápida

1. Configure o ambiente:

   ```bash
   python -m venv .venv
   . .venv/bin/activate  # Linux/macOS
   # ou .venv\\Scripts\\activate  # Windows PowerShell
   ```

2. Instale as dependências:

   ```bash
   python -m pip install --upgrade pip
   python -m pip install -e ".[dev]"
   ```

3. Copie o arquivo de exemplo de ambiente:

   ```bash
   copy .env.example .env
   ```

4. Para habilitar login com Google, defina `GOOGLE_OAUTH_CLIENT_ID` e `GOOGLE_OAUTH_CLIENT_SECRET` no `.env` e configure a URL de callback `/accounts/google/login/callback/` no cliente OAuth. Sem essas credenciais, o login por e-mail continua disponível.

5. Aplique as migrações:

   ```bash
   python src/manage.py migrate
   ```

6. Inicie o servidor local:

   ```bash
   python src/manage.py runserver
   ```

## Docker Compose

Para levantar a infraestrutura completa localmente:

```bash
docker compose up --build
```

Os serviços incluídos são:

- `django-app`
- `postgres`
- `redis`
- `celery-worker`
- `celery-beat`

## Testes

```bash
pytest
```

## Verificação de qualidade

```bash
ruff check .
python src/manage.py check
```

## Observações importantes

- O arquivo `.env` deve permanecer fora do controle de versão.
- A configuração de produção usa valores mais restritivos e exige que `DEBUG` seja `False`.
- O login Google depende de credenciais OAuth fornecidas fora do repositório e de homologação do fluxo.
- A execução dos serviços Docker, a homologação de produção e a restauração de backups devem ser verificadas antes de considerar o projeto pronto para produção.
- Funcionalidades planejadas ou parcialmente implementadas não devem ser consideradas integralmente disponíveis.

## Documentação

O arquivo `spec.md` é a fonte de verdade para os requisitos funcionais, decisões técnicas, regras de negócio, critérios de aceite e planejamento das fases.

Consulte também a pasta `docs/` para documentação operacional complementar.
