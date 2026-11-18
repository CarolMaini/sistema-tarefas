# Organizador

**Uma plataforma web para organizar atividades, planejar rotinas, colaborar em espaços compartilhados e acompanhar a execução do trabalho.**

O Organizador é um projeto autoral em desenvolvimento, criado para ir além de uma lista convencional de tarefas. A aplicação permite estruturar atividades individuais e compartilhadas, definir responsabilidades, planejar recorrências e registrar a execução das atividades.

🪧 **Vitrine.Dev** | 
--- | ---
✨ **Nome** | Organizador
🏷️ **Tecnologias** | Python, Django, PostgreSQL, SQLite, HTML, Tailwind CSS, JavaScript, Celery, Redis, Docker, pytest
🚀 **URL** | [Repositório no GitHub](https://github.com/CarolMaini/sistema-tarefas) — aplicação ainda sem deploy público
🔥 **Desafio** | Projeto autoral

## 🔨 Funcionalidades do projeto

O projeto está em desenvolvimento incremental. Os itens abaixo distinguem funcionalidades já implementadas no código das que ainda estão em evolução ou planejamento.

| Funcionalidade | Estado atual |
|---|---|
| Cadastro, autenticação por e-mail e senha e redefinição de senha | Implementada |
| Login social com Google | Configurado; depende de credenciais OAuth e homologação |
| Espaços de trabalho, membros e papéis | Parcialmente implementada |
| Criação de atividades e atribuição de responsáveis às ocorrências | Parcialmente implementada |
| Recorrências semanais, quinzenais e mensais | Implementada no código; critérios de aceite ainda precisam de validação completa |
| Geração de ocorrências e calendário mensal | Implementada no código; validação funcional em andamento |
| Registro de execução, horários, comentários e anexos | Parcialmente implementada |
| Auditoria de alterações | Parcialmente implementada |
| Central de notificações e envio assíncrono de e-mails | Planejada |
| Homologação e publicação em produção | Pendente |

## ✔️ Técnicas e tecnologias utilizadas

- **Python 3.12** — linguagem principal.
- **Django 6.1.3** — framework web e organização da aplicação.
- **PostgreSQL** — banco de dados principal previsto para produção.
- **SQLite** — banco utilizado no desenvolvimento local.
- **Django Templates, HTML e Tailwind CSS** — camada de apresentação.
- **JavaScript** — interações pontuais no front-end.
- **Django Allauth** — autenticação e integração com login social.
- **Celery e Redis** — infraestrutura preparada para processamento assíncrono e tarefas agendadas.
- **Docker Compose** — orquestração do ambiente local.
- **pytest e pytest-django** — testes automatizados.
- **Ruff** — análise estática e padronização do código.
- **GitHub Actions** — automação de verificações de qualidade.

A arquitetura segue o modelo de monólito modular Django, com separação de responsabilidades por aplicações:

- `accounts`: identidade e autenticação.
- `access`: permissões e controle de acesso.
- `workspaces`: espaços de trabalho, membros e papéis.
- `tasks`: atividades e atribuições.
- `scheduling`: recorrências, ocorrências e calendário.
- `notifications`: notificações.
- `audit`: registros de auditoria.
- `dashboard`: visão geral e acompanhamento.

## 📁 Acesso ao projeto

O código-fonte está disponível publicamente no GitHub:

[CarolMaini/sistema-tarefas](https://github.com/CarolMaini/sistema-tarefas)

## 🛠️ Abrir e rodar o projeto

### Requisitos

- Python 3.12
- pip
- Docker e Docker Compose (opcionais para executar os serviços auxiliares)

### Execução local

1. Clone o repositório e entre na pasta do projeto:

   ```bash
   git clone https://github.com/CarolMaini/sistema-tarefas.git
   cd sistema-tarefas
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   # Linux/macOS
   source .venv/bin/activate
   # Windows PowerShell
   .venv\\Scripts\\Activate.ps1
   ```

3. Instale as dependências:

   ```bash
   python -m pip install --upgrade pip
   python -m pip install -e ".[dev]"
   ```

4. Copie o arquivo de exemplo de ambiente e ajuste as variáveis necessárias:

   ```bash
   cp .env.example .env
   ```

   No Windows, utilize `copy .env.example .env`.

5. Aplique as migrações e inicie o servidor:

   ```bash
   python src/manage.py migrate
   python src/manage.py runserver
   ```

6. Acesse [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Execução com Docker Compose

Com o arquivo `.env` configurado, execute:

```bash
docker compose up --build
```

O ambiente define serviços para Django, PostgreSQL, Redis, Celery Worker e Celery Beat.

### Testes e qualidade

Execute os testes automatizados:

```bash
pytest
```

Verifique a qualidade e a configuração do Django:

```bash
ruff check .
python src/manage.py check
```

### Configuração opcional do Google

Para habilitar o login com Google, configure `GOOGLE_OAUTH_CLIENT_ID` e `GOOGLE_OAUTH_CLIENT_SECRET` no arquivo `.env`, além da URL de callback `/accounts/google/login/callback/` no cliente OAuth. Sem essas credenciais, a autenticação por e-mail e senha continua disponível.

## 📚 Documentação e próximos passos

O arquivo [spec.md](spec.md) é a fonte de verdade dos requisitos funcionais, regras de negócio, critérios de aceite, decisões técnicas e planejamento das fases. A pasta `docs/` contém documentação operacional complementar.

O projeto ainda não está publicado em produção. Funcionalidades identificadas como parciais ou planejadas não devem ser consideradas integralmente disponíveis. Antes de uma publicação, ainda são necessárias validações funcionais e operacionais, revisão de segurança, configuração de produção, monitoramento e testes de restauração de backups.

---

#vitrinedev
