# Sistema de Gerenciamento de TI - SISInfo V2 💻⚙️

<div align="center">
<img src="https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2/raw/main/.gitassets/capa.png" width="350" />

<div data-badges>
    <img src="https://img.shields.io/github/stars/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2?style=for-the-badge" alt="GitHub stars" />
    <img src="https://img.shields.io/github/forks/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2?style=for-the-badge" alt="GitHub forks" />
    <img src="https://img.shields.io/github/issues/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2?style=for-the-badge" alt="GitHub issues" />
</div>

<div data-badges>
    <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python" />
    <img src="https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
    <img src="https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS" />
    <img src="https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white" alt="Postgres" />
    <img src="https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB" />
    <img src="https://img.shields.io/badge/htmx-3D72D7?style=for-the-badge&logo=htmx&logoColor=white" alt="HTMX" />
    <img src="https://img.shields.io/badge/Alpine.js-8BC0D0?style=for-the-badge&logo=alpine.js&logoColor=black" alt="Alpine.js" />
</div>
</div>

<h3>🖥️ SISInfo: Sistema de Gerenciamento da Diretoria de TI 🖥️</h3>
O SISInfo V2 é uma plataforma robusta e modular desenvolvida para a Diretoria de Tecnologia da Informação da Prefeitura de Novo Horizonte. O sistema centraliza a gestão de ativos, licitações, fornecedores, estrutura organizacional e relatórios, promovendo eficiência e transparência.

### 📋 Funcionalidades Principais
- **Autenticação e Controle de Acesso**: Gestão de usuários com perfis diferenciados (Admin, Técnico) e sistema de onboarding.
- **Sistema de Auditoria**: Rastreamento completo de operações com MongoDB Atlas para compliance.
- **Gestão de Licitações e Fornecedores**: Controle completo de processos licitatórios e base de fornecedores.
- **Estrutura Organizacional**: Mapeamento de diretorias e setores da prefeitura.
- **Relatórios e Laudos**: Geração e gerenciamento de laudos técnicos e relatórios de materiais.
- **Dashboard**: Visão geral com indicadores chave de desempenho.

### 🏗️ Arquitetura
O projeto segue uma arquitetura **Service Layer** sobre o padrão MVT do Django, garantindo:
- **Separação de Responsabilidades**: Lógica de negócios encapsulada em serviços (`services.py`), mantendo as views leves.
- **Testabilidade**: Facilidade na criação de testes unitários e de integração.
- **Manutenibilidade**: Código organizado e documentado com docstrings e type hints.
- **Auditoria Automática**: Sistema de logs via signals para rastreamento de todas as operações.

## 🚀 Tecnologias
| Tecnologia | Versão | Descrição |
| :---------- | :--------- | :---------------------------------- |
| `Python` | `3.12.x` | Linguagem principal |
| `Django` | `5.2.6` | Framework Web |
| `PostgreSQL` | `Latest` | Banco de Dados Principal |
| `MongoDB` | `Atlas Free` | Logs de Auditoria |
| `TailwindCSS` | `3.4.x` | Estilização |
| `Alpine.js` | `3.13.3` | Reatividade Frontend |
| `HTMX` | `1.9.10` | Interações AJAX |
| `ApexCharts` | `Latest` | Gráficos e Dashboards |
| `Docker` | `Latest` | Containerização (Opcional) |

## 🛠️ Setup Local

### 1. Clonar o repositório
```bash
git clone https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2.git
cd sisinfo-v2
```

### 2. Configurar Ambiente
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
npm install
```

### 4. Configurar Variáveis de Ambiente
Copie o arquivo de exemplo e configure suas variáveis:
```bash
cp contrib/.env-sample .env
```

**Variáveis importantes:**
- `DATABASE_URL`: Conexão PostgreSQL
- `DATABASE_MONGODB_LOGS`: Conexão MongoDB Atlas (para auditoria)
- `SECRET_KEY`: Chave secreta Django
- `DEBUG`: True para desenvolvimento

### 5. Banco de Dados e Migrações
```bash
python manage.py migrate
```

### 6. Executar o Projeto
Em terminais separados:
```bash
# Compilar CSS (Tailwind)
npm run dev

# Rodar Servidor Django
python manage.py runserver
```
Acesse: `http://127.0.0.1:8000`

## 🔐 Sistema de Auditoria

O projeto inclui um sistema completo de auditoria com MongoDB:

### Comandos Disponíveis
```bash
# Backup de logs
python manage.py backup_audit_logs
python manage.py backup_audit_logs --days 30 --compress

# Limpeza de logs antigos
python manage.py clean_audit_logs --days 90 --dry-run
python manage.py clean_audit_logs --days 90 --backup-first
```

### Configuração MongoDB
1. Crie uma conta no [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Configure a string de conexão no `.env`:
   ```
   DATABASE_MONGODB_LOGS=mongodb+srv://user:password@cluster.mongodb.net/sisinfo_audit
   ```
3. Crie os índices recomendados (veja `docs/PROXIMOS_PASSOS.md`)

## 🧪 Testes
Para executar a suíte de testes:
```bash
# Todos os testes
python manage.py test

# App específico
python manage.py test authenticate

# Sem migrações (mais rápido)
python manage.py test --nomigrations
```

## 📚 Documentação

- **[GEMINI.md](docs/GEMINI.md)**: Guia completo para colaboração com IA
- **[PROXIMOS_PASSOS.md](docs/PROXIMOS_PASSOS.md)**: Roadmap e próximos passos
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Guia de contribuição

## 🤝 Como Contribuir
Quer contribuir? Ótimo! Leia nosso [Guia de Contribuição](CONTRIBUTING.md) para detalhes sobre nosso código de conduta e o processo de envio de pull requests.

## 🔧 Comandos Úteis

### Manutenção de Dados
```bash
# Diagnóstico completo
python manage.py diagnose_data

# Limpeza de duplicatas
python manage.py clean_duplicate_biddings
python manage.py clean_duplicate_materials
python manage.py consolidate_suppliers

# Relatórios
python manage.py report_all_materials
```

### Importação de Licitações
```bash
# Método preferencial (XLSX)
python manage.py import_bidding_from_xlsx arquivo.xlsx

# Sincronização com PDF
python manage.py sync_bidding_with_pdf arquivo.pdf

# Fallback (PDF direto)
python manage.py import_bidding_pdf arquivo.pdf
```

## 📸 Screenshots
![](https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2/raw/main/.gitassets/2.jpg)
![](https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2/raw/main/.gitassets/3.jpg)

---

**Desenvolvido com ❤️ pela Diretoria de TI - Prefeitura de Novo Horizonte/SP**