# GEMINI.MD: Guia de Colaboração em IA

Este documento fornece o contexto essencial para os modelos de IA que interagem com este projeto. A adesão a estas diretrizes garantirá a consistência e manterá a qualidade do código.

## 1. Visão Geral e Propósito do Projeto

*   **Objetivo Principal:** O SISInfo V2 é uma plataforma completa e intuitiva desenvolvida para otimizar e centralizar a gestão da Diretoria de Tecnologia da Informação da Prefeitura de Novo Horizonte. Ele oferece ferramentas para gerenciamento de ativos de TI, central de serviços de helpdesk, gestão de projetos de TI e geração de relatórios e análises.
*   **Domínio de Negócio:** Gestão Pública / Tecnologia da Informação Municipal.

## 2. Tecnologias e Pilha Principal

*   **Linguagens:** Python (3.12.x preferencial, 3.11.x compatível), JavaScript.
*   **Frameworks e Runtimes:**
    *   Backend: Django 5.2.6
    *   Frontend: Tailwind CSS 3.3.5, Flowbite 2.0.0
    *   Runtime: Node.js 20.9.0+ (para ferramentas de frontend)
*   **Bancos de Dados:** PostgreSQL (via Docker).
*   **Bibliotecas/Dependências Chave:**
    *   Python: `django`, `psycopg2-binary` (PostgreSQL adapter), `python-decouple` (configuração de ambiente), `django-filter`, `django-extensions`, `pillow`, `djlint`.
    *   JavaScript: `tailwindcss`, `prettier`, `prettier-plugin-tailwindcss`, `flowbite`.
*   **Gerenciadores de Pacotes:** `pip` (Python), `npm` (Node.js).

## 3. Padrões Arquiteturais

*   **Arquitetura Geral:** Aplicação Monolítica baseada em Django, seguindo o padrão Model-View-Template (MVT). O projeto é modularizado através de "apps" Django, cada um encapsulando uma funcionalidade específica.
*   **Filosofia da Estrutura de Diretórios:**
    *   `/core`: Contém as configurações globais do projeto Django (settings, urls, wsgi, asgi).
    *   `/authenticate`: App Django para gerenciamento de autenticação e usuários.
    *   `/bidding_supplier`: App Django para gerenciamento de fornecedores e licitações.
    *   `/dashboard`: App Django para o painel principal e funcionalidades relacionadas.
    *   `/reports`: App Django para geração e gerenciamento de relatórios.
    *   `/static`: Contém arquivos estáticos (CSS, JS, imagens) servidos diretamente.
    *   `/templates`: Contém templates HTML base e templates compartilhados entre os apps.
    *   `/docs`: Contém a documentação do projeto.
    *   `/.docker`: Contém configurações para serviços Docker (ex: PostgreSQL).
    *   `/.venv`: Ambiente virtual Python.
    *   `contrib`: Arquivos auxiliares, como `.env-sample`.

## 4. Convenções de Codificação e Guia de Estilo

*   **Formatação:**
    *   Geral: `charset = utf-8`, `insert_final_newline = true`, `end_of_line = lf`, `indent_style = space`, `indent_size = 4`.
    *   Python: Adere ao guia de estilo [PEP 8](https://www.python.org/dev/peps/pep-0008/).
    *   JavaScript/CSS: Formatado automaticamente com [Prettier](https://prettier.io/), utilizando `prettier-plugin-tailwindcss`.
    *   Templates Django: Utiliza `djlint` para linting.
*   **Convenções de Nomenclatura:**
    *   Variáveis e Funções Python: `snake_case` (ex: `minha_variavel`, `minha_funcao`).
    *   Classes Python: `PascalCase` (ex: `MinhaClasse`).
    *   Arquivos Python: `snake_case` (ex: `views.py`, `models.py`).
    *   Arquivos JavaScript/CSS: `kebab-case` ou `snake_case` (inferido).
*   **Design de API:** O projeto é predominantemente uma aplicação web renderizada no servidor (Server-Side Rendered - SSR) com Django. Não há indícios de uma API RESTful explícita para consumo externo.
*   **Tratamento de Erros:** (Inferido) Segue as práticas padrão do Django para tratamento de exceções e exibição de mensagens ao usuário.

## 5. Arquivos Chave e Pontos de Entrada

*   **Ponto(s) de Entrada Principal:**
    *   `manage.py`: Script principal para comandos de gerenciamento Django (execução do servidor de desenvolvimento, migrações, testes).
    *   `core/wsgi.py`: Ponto de entrada para servidores web compatíveis com WSGI.
*   **Configuração:**
    *   `core/settings.py`: Configurações principais do Django.
    *   `.env`: Variáveis de ambiente (baseado em `contrib/.env-sample`).
    *   `docker-compose.yaml`: Configuração dos serviços Docker (ex: banco de dados).
*   **Pipeline CI/CD:** Não foi identificado um arquivo de configuração de pipeline CI/CD (ex: `.github/workflows`, `.gitlab-ci.yml`) na estrutura de diretórios fornecida.

## 6. Fluxo de Trabalho de Desenvolvimento e Testes

*   **Ambiente de Desenvolvimento Local:**
    1.  Clonar o repositório.
    2.  Criar e ativar um ambiente virtual Python (`python -m venv .venv`).
    3.  Instalar dependências Python (`pip install -r requirements.txt`).
    4.  Instalar dependências Node.js (`npm install`).
    5.  Copiar e configurar o arquivo `.env` (`cp contrib/.env-sample .env`).
    6.  Executar migrações do banco de dados (`python manage.py migrate`).
    7.  Iniciar o compilador Tailwind CSS em um terminal (`npm run dev`).
    8.  Iniciar o servidor Django em outro terminal (`python manage.py runserver`).
*   **Testes:**
    *   Executar todos os testes: `python manage.py test`
    *   Executar testes de uma aplicação específica: `python manage.py test <app_name>`
    *   Novas funcionalidades e correções de bugs devem ser acompanhadas de testes correspondentes.
*   **Processo CI/CD:** Não identificado.

## 7. Instruções Específicas para Colaboração com IA

*   **Diretrizes de Contribuição:**
    *   Crie branches a partir da `main` com nomes descritivos (ex: `feat/nova-funcionalidade`, `fix/correcao-bug-x`).
    *   Faça commits atômicos com mensagens claras, seguindo a especificação de [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) (ex: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`).
    *   Garanta que suas alterações não quebrem funcionalidades existentes e adicione novos testes quando aplicável.
    *   Mantenha sua branch atualizada com a `main` antes de abrir um Pull Request (PR).
    *   Abra PRs para a branch `main`, descrevendo as alterações detalhadamente.
    *   Esteja aberto a feedback durante a revisão de código.
*   **Infraestrutura (IaC):** Não há um diretório dedicado a Infrastructure as Code (IaC) no projeto. Quaisquer alterações na infraestrutura (ex: Docker Compose) devem ser revisadas cuidadosamente.
*   **Segurança:** Seja sempre consciente da segurança. Não codifique segredos ou chaves diretamente no código. Utilize variáveis de ambiente (via `.env` e `python-decouple`) para informações sensíveis. Garanta que quaisquer alterações na lógica de autenticação sejam seguras e validadas.
*   **Dependências:**
    *   Para dependências Python: Adicione ao `requirements.txt` e execute `pip install -r requirements.txt`.
    *   Para dependências Node.js/Frontend: Adicione ao `package.json` e execute `npm install`.
*   **Mensagens de Commit:** **É mandatório** seguir a especificação de Conventional Commits. Isso é crucial para manter um histórico de commits limpo e facilitar a automação de tarefas como a geração de changelogs.
