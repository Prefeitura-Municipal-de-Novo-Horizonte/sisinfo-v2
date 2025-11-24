# Guia de Contribuição - SISInfo V2

Obrigado por contribuir com o SISInfo V2! Este guia ajudará você a configurar o ambiente e entender nosso fluxo de trabalho.

## 📋 Índice

- [Setup do Ambiente](#setup-do-ambiente)
- [Padrões de Código](#padrões-de-código)
- [Fluxo de Trabalho Git](#fluxo-de-trabalho-git)
- [Processo de Pull Request](#processo-de-pull-request)
- [Testes](#testes)

## 🚀 Setup do Ambiente

### Requisitos

- Python 3.12.x (recomendado) ou 3.11.x
- Node.js 20.9.0+
- PostgreSQL (via Supabase)
- Git

### Configuração Inicial

1. **Fork e clone o repositório**

```bash
git clone https://github.com/SEU-USUARIO/sisinfo-v2.git
cd sisinfo-v2
```

2. **Crie um ambiente virtual**

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\\Scripts\\activate.bat  # Windows
```

3. **Instale as dependências**

```bash
pip install --upgrade pip
pip install -r requirements.txt
npm install
```

4. **Configure as variáveis de ambiente**

```bash
cp contrib/.env-sample .env
```

Edite `.env` com suas credenciais de desenvolvimento.

5. **Execute as migrações**

```bash
python manage.py migrate
```

6. **Crie um superusuário**

```bash
python manage.py createsuperuser
```

7. **Rode o servidor de desenvolvimento**

Terminal 1:
```bash
npm run dev
```

Terminal 2:
```bash
python manage.py runserver
```

## 📝 Padrões de Código

### Python

- **PEP 8**: Siga o guia de estilo Python
- **Docstrings**: Adicione docstrings em classes e funções complexas
- **Type Hints**: Use quando apropriado
- **Imports**: Organize em ordem alfabética

Exemplo:
```python
def calculate_total_price(price: Decimal, readjustment: float) -> Decimal:
    """
    Calcula o preço total com reajuste aplicado.
    
    Args:
        price: Preço base do material
        readjustment: Percentual de reajuste (ex: 10 para 10%)
    
    Returns:
        Preço total com reajuste aplicado
    """
    if readjustment == 0:
        return price
    
    total = float(price) + (float(price) * (readjustment / 100))
    return Decimal(str(total)).quantize(Decimal("0.00"))
```

### Django

- **Models**: Use `verbose_name` e `help_text`
- **Views**: Prefira Class-Based Views quando apropriado
- **Templates**: Use template tags do Django, evite lógica complexa
- **Migrations**: Sempre crie migrações localmente, nunca em produção

### JavaScript/CSS

- **Prettier**: Código formatado automaticamente
- **TailwindCSS**: Use classes utilitárias, evite CSS customizado
- **Flowbite**: Use componentes prontos quando possível

## 🌳 Fluxo de Trabalho Git

### Branches

- `main`: Código em produção (protegida)
- `dev`: Branch de desenvolvimento
- `feat/*`: Novas funcionalidades
- `fix/*`: Correções de bugs
- `docs/*`: Documentação
- `refactor/*`: Refatorações

### Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat: adicionar campo status em Bidding
fix: corrigir erro de slug vazio em Material
docs: atualizar README com versões atuais
refactor: migrar views para CBVs
test: adicionar testes para MaterialBidding
chore: atualizar dependências
```

### Workflow

1. **Crie uma branch a partir de `dev`**

```bash
git checkout dev
git pull origin dev
git checkout -b feat/minha-funcionalidade
```

2. **Faça commits atômicos**

```bash
git add .
git commit -m "feat: adicionar validação de CPF"
```

3. **Mantenha sua branch atualizada**

```bash
git fetch origin
git rebase origin/dev
```

4. **Push para o seu fork**

```bash
git push origin feat/minha-funcionalidade
```

## 🔄 Processo de Pull Request

### Antes de Abrir o PR

- [ ] Código segue os padrões estabelecidos
- [ ] Testes passam (`python manage.py test`)
- [ ] Migrações criadas e testadas
- [ ] Documentação atualizada (se aplicável)
- [ ] Sem conflitos com `dev`

### Template de PR

```markdown
## Descrição

Breve descrição das mudanças.

## Tipo de Mudança

- [ ] Bug fix
- [ ] Nova funcionalidade
- [ ] Breaking change
- [ ] Documentação

## Como Testar

1. Passo 1
2. Passo 2
3. Resultado esperado

## Checklist

- [ ] Código segue os padrões do projeto
- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada
- [ ] Sem warnings de lint
```

### Revisão

- PRs precisam de pelo menos 1 aprovação
- Responda aos comentários prontamente
- Faça as alterações solicitadas
- Mantenha o PR focado (evite mudanças não relacionadas)

## 🧪 Testes

### Rodar Testes

```bash
# Todos os testes
python manage.py test

# App específico
python manage.py test dashboard

# Teste específico
python manage.py test dashboard.tests.TestMaterialModel
```

### Escrever Testes

```python
from django.test import TestCase
from dashboard.models import Material

class MaterialModelTest(TestCase):
    def setUp(self):
        self.material = Material.objects.create(
            name="Material Teste",
            price=100.00
        )
    
    def test_total_price_without_readjustment(self):
        """Preço total sem reajuste deve ser igual ao preço base"""
        self.assertEqual(self.material.total_price(), Decimal("100.00"))
    
    def test_total_price_with_readjustment(self):
        """Preço total com 10% de reajuste deve ser 110.00"""
        self.material.readjustment = 10
        self.assertEqual(self.material.total_price(), Decimal("110.00"))
```

## 🐛 Reportar Bugs

Use o template de issue do GitHub:

1. **Descrição clara** do problema
2. **Passos para reproduzir**
3. **Comportamento esperado vs atual**
4. **Screenshots** (se aplicável)
5. **Ambiente** (OS, Python version, etc.)

## 💡 Sugestões de Funcionalidades

1. Verifique se já não existe uma issue similar
2. Descreva o problema que a funcionalidade resolve
3. Proponha uma solução
4. Aguarde feedback antes de implementar

## 📞 Contato

- **Issues**: Use o GitHub Issues
- **Discussões**: Use GitHub Discussions
- **Email**: [contato da prefeitura]

---

**Obrigado por contribuir! 🎉**
