# SISInfo V2 💻

<div align="center">
<img src="https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2/raw/main/.gitassets/capa.png" width="350" />

<p><strong>Sistema Integrado de Gestão da Diretoria de TI</strong></p>

<div data-badges>
    <img src="https://img.shields.io/github/stars/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2?style=for-the-badge" alt="GitHub stars" />
    <img src="https://img.shields.io/github/forks/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2?style=for-the-badge" alt="GitHub forks" />
    <img src="https://img.shields.io/github/issues/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2?style=for-the-badge" alt="GitHub issues" />
</div>

<div data-badges>
    <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python" />
    <img src="https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
    <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase" />
    <img src="https://img.shields.io/badge/vercel-%23000000.svg?style=for-the-badge&logo=vercel&logoColor=white" alt="Vercel" />
    <img src="https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS" />
    <img src="https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white" alt="Postgres" />
</div>
</div>

---

## � Sobre o Projeto

O **SISInfo V2** é uma plataforma completa desenvolvida para a **Diretoria de Tecnologia da Informação** da Prefeitura de Novo Horizonte/SP. O sistema centraliza a gestão de processos internos, proporcionando eficiência e transparência nas operações diárias.

### ✨ Principais Funcionalidades

| Módulo | Descrição |
|--------|-----------|
| **📊 Dashboard** | Visão geral com indicadores de desempenho e gráficos interativos |
| **📄 Laudos Técnicos** | Criação, gerenciamento e geração de PDFs de laudos de equipamentos |
| **🧾 Notas Fiscais** | Controle de notas fiscais com OCR automático via Gemini AI |
| **📦 Licitações** | Gestão completa de processos licitatórios e materiais |
| **🏢 Fornecedores** | Base de dados de fornecedores com consolidação automática |
| **�️ Estrutura Organizacional** | Mapeamento de diretorias e setores da prefeitura |
| **👥 Autenticação** | Sistema de usuários com perfis diferenciados e onboarding |
| **📝 Auditoria** | Rastreamento completo de operações (MongoDB) |

---

## 🚀 Tecnologias

### Backend
- **Python 3.12** + **Django 5.2** - Framework principal
- **PostgreSQL** (Supabase) - Banco de dados relacional
- **MongoDB Atlas** - Logs de auditoria

### Frontend
- **TailwindCSS 3.4** - Estilização
- **Alpine.js 3.13** - Reatividade
- **HTMX 1.9** - Interações AJAX sem JavaScript
- **ApexCharts** - Gráficos e dashboards

### Serviços
- **Supabase** - Storage e Edge Functions
- **Gemini API 2.0** - OCR de notas fiscais
- **Browserless.io** - Geração de PDFs
- **Vercel** - Deploy e hosting

---

## 🛠️ Instalação

### Pré-requisitos
- Python 3.11+
- Node.js 20+
- Docker (opcional, para Supabase local)

### 1. Clone o repositório
```bash
git clone https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2.git
cd sisinfo-v2
```

### 2. Configure o ambiente Python
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### 3. Configure o ambiente Node.js
```bash
npm install
```

### 4. Configure as variáveis de ambiente
```bash
cp contrib/.env-sample .env
# Edite o .env com suas configurações
```

### 5. Execute as migrações
```bash
python manage.py migrate
```

### 6. Inicie o servidor
```bash
# Terminal 1: Tailwind CSS
npm run dev

# Terminal 2: Django
python manage.py runserver
```

Acesse: **http://127.0.0.1:8000**

---

## ⚙️ Configuração

### Variáveis de Ambiente Essenciais

| Variável | Descrição |
|----------|-----------|
| `SECRET_KEY` | Chave secreta do Django |
| `DEBUG` | `True` para desenvolvimento |
| `POSTGRES_URL_NON_POOLING` | URL de conexão PostgreSQL |
| `SUPABASE_URL` | URL do projeto Supabase |
| `SUPABASE_ANON_KEY` | Chave pública do Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Chave de serviço (admin) |
| `DATABASE_MONGODB_LOGS` | String de conexão MongoDB |
| `GEMINI_API_KEY` | Chave(s) da API Gemini |
| `BROWSERLESS_API_KEY` | Token do Browserless.io |

### Supabase Local (Opcional)

Para desenvolvimento com Supabase local:
```bash
npx supabase start
```

Configure no `.env`:
```env
SUPABASE_URL=http://127.0.0.1:54321
CALLBACK_BASE_URL=http://host.docker.internal:8000
```

---

## 🧪 Testes

```bash
# Todos os testes
python manage.py test

# App específico
python manage.py test reports

# Sem migrações (mais rápido)
python manage.py test --nomigrations
```

---

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [OCR.md](docs/OCR.md) | Sistema de OCR com Supabase Edge Functions |
| [DEPLOY_OCR.md](docs/DEPLOY_OCR.md) | Checklist de deploy do OCR |
| [DOCKER.md](docs/DOCKER.md) | Configuração com Docker |
| [GEMINI.md](docs/GEMINI.md) | Guia para colaboração com IA |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Guia de contribuição |

---

## 🏗️ Arquitetura

```
sisinfo-v2/
├── authenticate/      # Autenticação e usuários
├── audit/             # Sistema de auditoria (MongoDB)
├── bidding_procurement/ # Licitações e materiais
├── bidding_supplier/  # Fornecedores
├── core/              # Configurações Django
├── dashboard/         # Painel principal
├── fiscal/            # Notas fiscais e entregas
├── organizational_structure/ # Diretorias e setores
├── reports/           # Laudos técnicos
├── supabase/          # Edge Functions
│   └── functions/
│       └── process-ocr/  # OCR via Gemini
├── static/            # CSS, JS, imagens
├── templates/         # Templates HTML base
└── docs/              # Documentação
```

---

## 📸 Screenshots

<div align="center">
<img src="https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2/raw/main/.gitassets/2.jpg" width="45%" />
<img src="https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2/raw/main/.gitassets/3.jpg" width="45%" />
</div>

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Leia o [Guia de Contribuição](CONTRIBUTING.md) para detalhes sobre nosso código de conduta e processo de pull requests.

---

## 📄 Licença

Este projeto é de uso interno da Prefeitura Municipal de Novo Horizonte.

---

<div align="center">

**Desenvolvido com ❤️ pela Diretoria de TI**

Prefeitura Municipal de Novo Horizonte/SP

</div>