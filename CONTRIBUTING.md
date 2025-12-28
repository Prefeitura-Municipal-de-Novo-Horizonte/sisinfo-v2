# Guia de Contribuição - SISInfo V2

Obrigado por contribuir com o SISInfo V2! Este guia estabelece as práticas e padrões do projeto.

---

## Fluxo de Trabalho

### Branches
| Branch | Propósito |
|--------|-----------|
| `main` | Produção (estável) - **Nunca commite diretamente** |
| `dev` | Integração/Staging - PRs vão para cá |

### Ciclo de Desenvolvimento

1. **Sincronize seu fork:**
   ```bash
   git fetch upstream
   git checkout dev
   git merge upstream/dev
   ```

2. **Crie uma branch:**
   ```bash
   git checkout -b feat/minha-feature   # Nova funcionalidade
   git checkout -b fix/meu-bug          # Correção
   git checkout -b docs/minha-doc       # Documentação
   ```

3. **Desenvolva e teste:**
   ```bash
   python manage.py test --nomigrations
   ```

4. **Abra o PR:**
   - De `seu-fork/feat/minha-feature` para `repo-oficial/dev`
   - Preencha o template do PR

---

## Ambiente de Desenvolvimento

### Pré-requisitos
- Python 3.12+ (3.11 compatível)
- Node.js 20+
- Docker Desktop

### Setup Rápido
```bash
# 1. Clone e instale
git clone <seu-fork-url>
cd sisinfo-v2
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install

# 2. Configure variáveis
cp contrib/.env-sample .env
# Edite o .env

# 3. Banco de dados
docker-compose up -d
python manage.py migrate

# 4. Execute
npm run dev          # Terminal 1: Tailwind
python manage.py runserver  # Terminal 2: Django
```

### Supabase Local (OCR)
```bash
npx supabase start
npx supabase functions serve process-ocr --no-verify-jwt
```

> **Nota:** Sem Supabase, defina `USE_SUPABASE_STORAGE=False` no `.env`

---

## Padrões de Código

### Python
- Siga [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use `snake_case` para variáveis/funções
- Use `PascalCase` para classes
- Adicione docstrings e type hints

### JavaScript/CSS
- Formatado com Prettier

### Templates
- Use `djlint` para linting

### Commits (Obrigatório)
Use [Conventional Commits](https://www.conventionalcommits.org/):
```
feat(auth): adicionar sistema de onboarding
fix(audit): corrigir conexão MongoDB
docs: atualizar README
refactor(fiscal): melhorar service de OCR
test(reports): adicionar testes de PDF
```

---

## Testes

**Obrigatório antes de abrir PR:**

```bash
# Testes rápidos (desenvolvimento)
python manage.py test --nomigrations

# Testes completos (antes do PR)
python manage.py test

# App específico
python manage.py test authenticate
```

### Escrevendo Testes
- Crie em `tests.py` ou `tests/test_*.py`
- Cubra casos de sucesso e erro
- Mantenha cobertura acima de 70%

---

## Arquitetura

### Service Layer Pattern
```python
# views.py
def create_user(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        user = AuthenticateService.create_user(form)  # Service
        return redirect('dashboard:index')
    return render(request, 'form.html', {'form': form})
```

| Camada | Arquivo | Responsabilidade |
|--------|---------|------------------|
| Models | `models.py` | Definição de dados |
| Services | `services.py` | Lógica de negócios |
| Views | `views.py` | Orquestração HTTP |
| Forms | `forms.py` | Validação de entrada |

---

## Sistema de Auditoria

Logs automáticos de CREATE, UPDATE, DELETE e autenticação.

### Adicionar Modelo à Auditoria
Edite `audit/signals.py`:
```python
AUDITED_MODELS = [
    'ProfessionalUser',
    'Bidding',
    'SeuNovoModelo',  # Adicione aqui
]
```

---

## Checklist do PR

- [ ] Código segue PEP 8
- [ ] Testes passando
- [ ] Docstrings atualizadas
- [ ] Commits seguem Conventional Commits
- [ ] Sem conflitos com `dev`
- [ ] PR template preenchido

---

## Documentação

| Documento | Descrição |
|-----------|-----------|
| [docs/OCR.md](docs/OCR.md) | Sistema de OCR |
| [docs/DOCKER.md](docs/DOCKER.md) | Configuração Docker |
| [docs/GEMINI.md](docs/GEMINI.md) | Contexto para IA |
| [docs/PROXIMOS_PASSOS.md](docs/PROXIMOS_PASSOS.md) | Roadmap |

---

## Contato

- **Issues:** GitHub Issues
- **Email:** ti@novohorizonte.sp.gov.br

---

**Obrigado por contribuir! 🚀**
