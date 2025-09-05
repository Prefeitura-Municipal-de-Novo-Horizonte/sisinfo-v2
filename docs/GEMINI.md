# GEMINI.MD: Guia de Colaboração em IA

Este documento fornece o contexto essencial para os modelos de IA que interagem com este projeto. A adesão a estas diretrizes garantirá a consistência e manterá a qualidade do código.

## 1. Project Overview & Purpose

*   **Primary Goal:** O SISInfo V2 é um sistema de gerenciamento de TI desenvolvido para otimizar e centralizar a gestão da Diretoria de Tecnologia da Informação da Prefeitura de Novo Horizonte. Ele oferece ferramentas para gerenciamento de ativos de TI, central de serviços de helpdesk, gestão de projetos de TI e relatórios/análises.
*   **Business Domain:** Gestão de TI no Setor Público (Governo Municipal).

## 2. Core Technologies & Stack

*   **Languages:** Python (preferencialmente 3.12, compatível com 3.11.x), JavaScript, Bash Script.
*   **Frameworks & Runtimes:** Django, Node.js (v20.9.0).
*   **Databases:** PostgreSQL (inferido de `requirements.txt` e `core/settings.py`).
*   **Key Libraries/Dependencies:**
    *   **Python:** `django`, `django-extensions`, `django-filter`, `python-decouple`, `psycopg2-binary`, `pillow`, `urllib3`, `cpf-cnpj-validate`, `dj_static`, `dj-database-url`.
    *   **JavaScript:** `tailwindcss`, `flowbite`, `prettier`, `prettier-plugin-tailwind-css`.
*   **Package Manager(s):** `pip` (para Python), `npm` (para JavaScript).

## 3. Architectural Patterns

*   **Overall Architecture:** Aplicação Monolítica (inferido da estrutura de projeto Django com múltiplos apps dentro de um único repositório).
*   **Directory Structure Philosophy:**
    *   `/authenticate`, `/bidding_supplier`, `/dashboard`, `/reports`: Aplicações Django, provavelmente representando diferentes módulos/funcionalidades do sistema.
    *   `/core`: Configuração principal do projeto Django (settings, URLs).
    *   `/static`: Arquivos estáticos (CSS, JS, imagens).
    *   `/templates`: Templates Django globais.
    *   `/docs`: Contém documentação do projeto, incluindo este `GEMINI.md`.
    *   `/.gitassets`: Contém imagens usadas na documentação.
    *   `/contrib`: Contém arquivos de contribuição, como `.env-sample`.

## 4. Coding Conventions & Style Guide

*   **Formatting:** `prettier` e `prettier-plugin-tailwind-css` são usados para formatação de arquivos frontend. `djlint` é usado para linting de templates Django. Para Python, espera-se o estilo padrão do PEP 8, embora não haja uma ferramenta de formatação explícita configurada.
*   **Naming Conventions:** Não explicitamente definidas. Para Python, espera-se `snake_case` para variáveis/funções e `PascalCase` para classes. Para o frontend, `camelCase` ou `kebab-case` são prováveis, com base nas ferramentas de frontend.
*   **API Design:** Não explicitamente definida. O projeto parece ser renderizado no servidor usando o sistema de templates do Django.
*   **Error Handling:** Não explicitamente definido. Espera-se o uso de `try...except` em Python e o tratamento de erros padrão do Django.

## 5. Key Files & Entrypoints

*   **Main Entrypoint(s):** `manage.py` (para comandos Django), `core/wsgi.py` (para o servidor web).
*   **Configuration:** `core/settings.py`, `.env` (baseado em `contrib/.env-sample`).
*   **CI/CD Pipeline:** Não foram encontrados arquivos de configuração de CI/CD explícitos (ex: `.github/workflows`).

## 6. Development & Testing Workflow

*   **Local Development Environment:**
    1.  Clonar o repositório (`git clone`).
    2.  Criar e ativar um ambiente virtual Python (`python -m venv .venv`, `source .venv/bin/activate` ou `.venv\Scripts\activate.bat`).
    3.  Instalar dependências Python (`pip install -r requirements.txt`).
    4.  Instalar dependências JavaScript (`npm install`).
    5.  Copiar e configurar o arquivo de variáveis de ambiente (`cp contrib/.env-sample .env`).
    6.  Iniciar o observador do TailwindCSS (`npm run dev`).
    7.  Iniciar o servidor Django (`python manage.py runserver`).
*   **Testing:** O arquivo `TESTING.md` está vazio, indicando que não há instruções de teste explícitas. Espera-se o uso do framework de testes embutido do Django.
*   **CI/CD Process:** Não explicitamente definido.

## 7. Specific Instructions for AI Collaboration

*   **Contribution Guidelines:** O arquivo `CONTRIBUTING.md` está vazio. É necessário definir diretrizes claras para contribuições.
*   **Infrastructure (IaC):** Não há um diretório de IaC explícito. O `docker-compose.yaml` é usado para configuração do ambiente de desenvolvimento local.
*   **Security:** Chaves secretas e credenciais de banco de dados são gerenciadas via variáveis de ambiente (`python-decouple`). Não codificar informações sensíveis diretamente no código.
*   **Dependencies:** Novas dependências Python devem ser adicionadas ao `requirements.txt` e instaladas via `pip`. Novas dependências JavaScript devem ser adicionadas ao `package.json` e instaladas via `npm`.
*   **Commit Messages:** Não há um padrão de mensagens de commit definido. Recomenda-se adotar um padrão como Conventional Commits para clareza e automação.
