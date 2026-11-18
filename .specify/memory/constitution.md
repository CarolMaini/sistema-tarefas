<!--
Sync Impact Report
- Version change: 1.0.1 -> 1.0.2 (PATCH: align the declared Django version with the security-updated dependency)
- Modified principles: Arquitetura modular e simplicidade (stack baseline updated)
- Sections added: none
- Sections removed: none
- Follow-up TODO: confirm the original ratification date
-->
# Organizador de Tarefas Constitution

## Core Principles

### I. Arquitetura modular e simplicidade
- O projeto MUST utilizar Python 3.12 (>=3.12,<3.13), Django 6.1.3, PostgreSQL, Django Templates,
  HTML e Tailwind CSS.
- O projeto MUST utilizar Celery e Redis para processamento assíncrono e Docker Compose para orquestrar os serviços.
- A aplicação MUST adotar arquitetura monolítica modular, separada em aplicações Django.
- As views MUST priorizar Class-Based Views; exceções MUST ter justificativa técnica.
- Dependências e abstrações MUST ter propósito claro; complexidade desnecessária MUST ser evitada.

### II. Código sustentável e regras de negócio
- O código MUST seguir boas práticas de Python e Django, permanecer organizado e reutilizável e separar
	regras de negócio da apresentação. Regras ou código duplicados MUST ser evitados.
- As configurações MUST separar desenvolvimento e produção, e decisões arquiteturais relevantes MUST
	ser documentadas.
- O planejamento MUST suportar períodos semanais e mensais. Recorrências MUST suportar frequência
	semanal, quinzenal e mensal; a recorrência mensal MUST contemplar todos os sábados e domingos.
- Cada ocorrência MUST ter controle de conclusão independente por responsável. Ocorrências concluídas
	ou canceladas MUST manter seu histórico.
- As operações MUST preservar a integridade dos dados, evitar ocorrências duplicadas e usar transações
	quando a consistência depender de múltiplas alterações.

### III. Segurança e menor privilégio
- O sistema MUST usar um modelo de usuário próprio baseado em `AbstractUser`.
- A autenticação MUST oferecer login tradicional e autenticação com Google.
- Autenticação e autorização MUST ser verificadas no servidor, sob o princípio do menor privilégio.
- Permissões globais MUST ser distintas das permissões por workspace; usuários MUST ser impedidos de
	acessar dados de workspaces para os quais não tenham autorização.
- Senhas, tokens e credenciais MUST NOT ser versionados. Informações sensíveis MUST vir de variáveis
	de ambiente.
- As funcionalidades MUST aplicar proteções contra CSRF, XSS e acessos indevidos.

### IV. Processamento assíncrono e notificações
- Tarefas assíncronas MUST usar Celery com Redis como broker, e agendamentos periódicos MUST usar
	Celery Beat.
- Tarefas assíncronas MUST ser idempotentes sempre que possível. Falhas MUST ser tratadas e as
	tentativas de processamento MUST ser registradas.
- Notificações MUST estar disponíveis dentro da aplicação e por e-mail.

### V. Auditoria, arquivos e proteção de dados
- Ações importantes dos usuários MUST ser registradas para auditoria, sem incluir informações
	sensíveis nos logs.
- Arquivos MUST ficar em volume persistente no servidor e mídias MUST seguir o padrão
	`media/modelo/aaaa/mm/dd/`.
- Arquivos enviados MUST ser validados, e seu acesso MUST ser restringido a usuários autorizados.

## Qualidade e infraestrutura
- Os testes MUST usar pytest e pytest-django; Ruff MUST ser usado para qualidade e padronização do
	código.
- A suíte MUST cobrir regras de negócio, permissões e integridade dos dados.
- O Docker Compose MUST orquestrar Django, PostgreSQL, Redis, Celery Worker e Celery Beat.
- Desenvolvimento e produção MUST permanecer separados. A infraestrutura MUST prover logs, backups e
	verificações de saúde dos serviços.
- Uma funcionalidade MUST NOT ser considerada concluída sem testes e validações adequados.

## Desenvolvimento assistido por IA e conclusão
- Antes de alterar o sistema, agentes e colaboradores MUST analisar o código existente e compreender
	o propósito do código que pretendem substituir.
- O trabalho MUST respeitar esta Constitution, as especificações aprovadas e o escopo solicitado; não
	MUST implementar funcionalidades fora desse escopo.
- Dependências novas MUST ter justificativa. Decisões técnicas relevantes e alterações importantes
	MUST ser apresentadas e documentadas.
- Ninguém MUST afirmar que testes foram executados sem tê-los executado.
- Uma funcionalidade só estará concluída quando atender aos requisitos aprovados, respeitar esta
	Constitution, passar pelos testes relevantes e não apresentar regressões conhecidas.

## Governance
Esta Constitution define as regras obrigatórias do projeto. Alterações MUST ser justificadas,
documentadas e revisadas antes da aprovação; devem preservar segurança, qualidade e manutenibilidade.
Revisões de mudanças e de conclusão de funcionalidades MUST verificar conformidade com estes princípios
e com as especificações aprovadas. Testes e validações pertinentes MUST ser considerados nessa revisão.

As versões MUST seguir SemVer (`MAJOR.MINOR.PATCH`): MAJOR para remoções ou redefinições incompatíveis
de princípios; MINOR para novos princípios ou expansão material das regras; PATCH para esclarecimentos
sem alteração semântica. Alterações incompatíveis MUST registrar seus impactos e a migração necessária.

**Versão**: 1.0.2 | **Ratificada**: TODO(RATIFICATION_DATE): confirmar a data original de adoção | **Última alteração**: 2026-11-18
