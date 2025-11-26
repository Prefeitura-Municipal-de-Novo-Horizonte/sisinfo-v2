# Guia de Contribuição - SISInfo V2

Bem-vindo ao guia de contribuição do SISInfo V2! Este documento consolida as práticas de desenvolvimento, testes e fluxo de trabalho para garantir a qualidade e a organização do projeto.

## 🚀 Fluxo de Trabalho (Workflow)

Adotamos um fluxo baseado em **Feature Branches** e **Pull Requests**.

### 1. Branches Principais
*   **`main`**: Branch de **Produção**. Sempre estável. **Nunca commite diretamente nela.** Só recebe código via Pull Request da `dev`.
*   **`dev`**: Branch de **Integração/Staging**. Todo o desenvolvimento converge para cá. É onde testamos a integração de novas features.

### 2. Seu Ciclo de Desenvolvimento (Fork)
Recomendamos que você trabalhe em um **Fork** do repositório oficial.

1.  **Sincronize seu Fork:**
    ```bash
    git fetch upstream
    git checkout dev
    git merge upstream/dev
    ```
2.  **Crie uma Branch para a Tarefa:**
    *   Use nomes descritivos: `feat/nova-funcionalidade`, `fix/correcao-bug`, `refactor/melhoria-codigo`.
    ```bash
    git checkout -b feat/minha-tarefa
    ```
3.  **Desenvolva e Teste:**
    *   Siga o guia de estilo (PEP8 para Python).
    *   Rode os testes locais (veja seção de Testes).
4.  **Abra o Pull Request (PR):**
    *   Empurre sua branch: `git push origin feat/minha-tarefa`.
    *   No GitHub, abra o PR de **`seu-fork/feat/minha-tarefa`** para **`repo-oficial/dev`**.
    *   Preencha o template do PR com detalhes.

---

## 💻 Ambiente de Desenvolvimento

### Pré-requisitos
*   Python 3.12+
*   Node.js 20+
*   PostgreSQL (Docker recomendado)

### Configuração Rápida
1.  **Clone e Instale:**
    ```bash
    git clone <seu-fork-url>
    cd sisinfo-v2
    python -m venv .venv
    source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
    pip install -r requirements.txt
    npm install
    ```
2.  **Variáveis de Ambiente:**
    *   Copie `contrib/.env-sample` para `.env`.
    *   Configure `BROWSERLESS_API_KEY` se for trabalhar com geração de PDF.
3.  **Banco de Dados:**
    ```bash
    python manage.py migrate
    ```
4.  **Execução:**
    *   Terminal 1 (CSS): `npm run dev`
    *   Terminal 2 (Django): `python manage.py runserver`

---

## 🧪 Testes

A execução de testes é obrigatória antes de abrir um PR.

### Comandos
*   **Testes Rápidos (Sem Migrations):** Ideal para o dia a dia.
    ```bash
    python manage.py test --nomigrations
    ```
*   **Testes Completos (Obrigatório):** Simula o ambiente real.
    ```bash
    python manage.py test
    ```
*   **Testar App Específico:**
    ```bash
    python manage.py test reports
    ```

### Escrevendo Testes
*   Crie arquivos `tests.py` ou `tests/test_*.py` dentro de cada app.
*   Cubra casos de sucesso e erro.
*   Se criar uma nova feature, crie um teste para ela.

---

## 📄 Padrões de Projeto

*   **Código:** PEP8 (Python), Prettier (JS/CSS).
*   **Commits:** Use [Conventional Commits](https://www.conventionalcommits.org/). Ex: `feat: adicionar login`, `fix: corrigir erro 500`.
*   **Documentação:** Mantenha docstrings atualizadas em Models e Views.

---

## 🤖 Geração de PDF (Reports)
O sistema usa **Playwright** e **Browserless.io**.
*   Não use arquivos estáticos externos no template PDF; use Base64 ou CSS Inline.
*   Template: `reports/templates/pdf_download_template.html`.

---

Dúvidas? Abra uma Issue ou contate os mantenedores.
