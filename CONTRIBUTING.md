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
    *   Use nomes descritivos seguindo o padrão:
        - `feat/nome-da-feature` - Nova funcionalidade
        - `fix/nome-do-bug` - Correção de bug
        - `refactor/nome-da-melhoria` - Refatoração
        - `docs/nome-da-doc` - Documentação
        - `test/nome-do-teste` - Testes
    ```bash
    git checkout -b feat/minha-tarefa
    ```
3.  **Desenvolva e Teste:**
    *   Siga o guia de estilo (PEP8 para Python, Prettier para JS/CSS).
    *   Rode os testes locais (veja seção de Testes).
    *   Adicione docstrings e type hints em código Python.
4.  **Abra o Pull Request (PR):**
    *   Empurre sua branch: `git push origin feat/minha-tarefa`.
    *   No GitHub, abra o PR de **`seu-fork/feat/minha-tarefa`** para **`repo-oficial/dev`**.
    *   Preencha o template do PR com detalhes.
    *   Aguarde review e esteja aberto a feedback.

---

## 💻 Ambiente de Desenvolvimento

### Pré-requisitos
*   Python 3.12+ (3.11 compatível)
*   Node.js 20+
*   PostgreSQL (Docker recomendado)
*   MongoDB Atlas (Free Tier) - Para sistema de auditoria

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
    *   Configure as variáveis essenciais:
        - `DATABASE_URL`: PostgreSQL
        - `DATABASE_MONGODB_LOGS`: MongoDB Atlas (auditoria)
        - `SECRET_KEY`: Chave secreta Django
        - `DEBUG=True`: Para desenvolvimento
3.  **Banco de Dados:**
    ```bash
    python manage.py migrate
    ```
4.  **Execução:**
    *   Terminal 1 (CSS): `npm run dev`
    *   Terminal 2 (Django): `python manage.py runserver`

---

## 🧪 Testes

A execução de testes é **obrigatória** antes de abrir um PR.

### Comandos
*   **Testes Rápidos (Sem Migrations):** Ideal para o dia a dia.
    ```bash
    python manage.py test --nomigrations
    ```
*   **Testes Completos (Obrigatório antes do PR):** Simula o ambiente real.
    ```bash
    python manage.py test
    ```
*   **Testar App Específico:**
    ```bash
    python manage.py test authenticate
    python manage.py test audit
    ```

### Escrevendo Testes
*   Crie arquivos `tests.py` ou `tests/test_*.py` dentro de cada app.
*   Cubra casos de sucesso e erro.
*   **Se criar uma nova feature, crie um teste para ela.**
*   Use `TestCase` do Django para testes de models/views.
*   Mantenha cobertura de testes acima de 70%.

---

## 📄 Padrões de Projeto

### Código
*   **Python**: Siga [PEP 8](https://www.python.org/dev/peps/pep-0008/)
    - Use `snake_case` para variáveis e funções
    - Use `PascalCase` para classes
    - Adicione docstrings em classes e métodos
    - Use type hints sempre que possível
*   **JavaScript/CSS**: Formatado com [Prettier](https://prettier.io/)
*   **Templates Django**: Use `djlint` para linting

### Commits
*   **Obrigatório**: Use [Conventional Commits](https://www.conventionalcommits.org/)
*   Formato: `<tipo>(<escopo>): <descrição>`
*   Exemplos:
    ```
    feat(auth): adicionar sistema de onboarding
    fix(audit): corrigir verificação de collection no MongoDB
    docs: atualizar README com sistema de auditoria
    refactor(authenticate): melhorar docstrings e type hints
    test(audit): adicionar testes para AuditService
    ```

### Documentação
*   Mantenha docstrings atualizadas em Models, Views e Services.
*   Atualize `docs/PROXIMOS_PASSOS.md` ao completar tarefas.
*   Adicione comentários explicativos em lógica complexa.

---

## 🏗️ Arquitetura do Projeto

### Service Layer Pattern
O projeto usa **Service Layer** sobre o MVT do Django:
*   **Models** (`models.py`): Apenas definição de dados
*   **Services** (`services.py`): Lógica de negócios
*   **Views** (`views.py`): Orquestração e resposta HTTP
*   **Forms** (`forms.py`): Validação de entrada

### Exemplo de Fluxo
```python
# views.py
def create_user(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        user = AuthenticateService.create_user(form)  # Service layer
        AuditService.log_event('crud', request.user, 'ProfessionalUser', user.id, 'create')
        return redirect('dashboard:index')
    return render(request, 'form.html', {'form': form})
```

---

## 🔐 Sistema de Auditoria

### Logs Automáticos
O sistema registra automaticamente:
*   CREATE, UPDATE, DELETE de todos os modelos auditados
*   Login, logout, troca de senha
*   Mudanças (before/after) em atualizações

### Adicionar Modelo à Auditoria
Edite `audit/signals.py`:
```python
AUDITED_MODELS = [
    'ProfessionalUser',
    'Bidding',
    'Supplier',
    # Adicione seu modelo aqui
    'SeuNovoModelo',
]
```

### Comandos de Manutenção
```bash
# Backup de logs
python manage.py backup_audit_logs --days 30 --compress

# Limpeza de logs antigos
python manage.py clean_audit_logs --days 90 --backup-first
```

---

## 🤖 Geração de PDF (Reports)
O sistema usa **Playwright** e **Browserless.io**.
*   Não use arquivos estáticos externos no template PDF; use Base64 ou CSS Inline.
*   Template: `reports/templates/pdf_download_template.html`.

---

## 📚 Recursos Úteis

### Documentação Interna
*   [GEMINI.md](docs/GEMINI.md) - Guia para colaboração com IA
*   [PROXIMOS_PASSOS.md](docs/PROXIMOS_PASSOS.md) - Roadmap do projeto
*   [POS_DEPLOY_COMMANDS.md](docs/POS_DEPLOY_COMMANDS.md) - Comandos pós-deploy

### Ferramentas
*   **Linting**: `djlint` (templates), `prettier` (JS/CSS)
*   **Type Checking**: `mypy` (opcional)
*   **Testes**: Django TestCase

---

## ✅ Checklist Antes do PR

- [ ] Código segue PEP 8 e padrões do projeto
- [ ] Testes passando (`python manage.py test`)
- [ ] Docstrings adicionadas/atualizadas
- [ ] Commits seguem Conventional Commits
- [ ] Sem conflitos com branch `dev`
- [ ] PR template preenchido completamente
- [ ] Documentação atualizada (se aplicável)

---

## 🆘 Precisa de Ajuda?

*   **Issues**: Abra uma issue no GitHub
*   **Discussões**: Use GitHub Discussions
*   **Contato**: ti@novohorizonte.sp.gov.br

---

**Obrigado por contribuir com o SISInfo V2! 🚀**
