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
</div>
</div>

<h3>🖥️ SISInfo: Sistema de Gerenciamento da Diretoria de TI 🖥️</h3>
O SISInfo V2 é uma plataforma robusta e modular desenvolvida para a Diretoria de Tecnologia da Informação da Prefeitura de Novo Horizonte. O sistema centraliza a gestão de ativos, licitações, fornecedores, estrutura organizacional e relatórios, promovendo eficiência e transparência.

### 📋 Funcionalidades Principais
- **Autenticação e Controle de Acesso**: Gestão de usuários com perfis diferenciados (Admin, Técnico).
- **Gestão de Licitações e Fornecedores**: Controle completo de processos licitatórios e base de fornecedores.
- **Estrutura Organizacional**: Mapeamento de diretorias e setores da prefeitura.
- **Relatórios e Laudos**: Geração e gerenciamento de laudos técnicos e relatórios de materiais.
- **Dashboard**: Visão geral com indicadores chave de desempenho.

### 🏗️ Arquitetura
O projeto segue uma arquitetura **Service Layer** sobre o padrão MVT do Django, garantindo:
- **Separação de Responsabilidades**: Lógica de negócios encapsulada em serviços (`services.py`), mantendo as views leves.
- **Testabilidade**: Facilidade na criação de testes unitários e de integração.
- **Manutenibilidade**: Código organizado e documentado com docstrings e type hints.

## 🚀 Tecnologias
| Tecnologia | Versão | Descrição |
| :---------- | :--------- | :---------------------------------- |
| `Python` | `3.12.x` | Linguagem principal |
| `Django` | `5.2.6` | Framework Web |
| `PostgreSQL` | `Latest` | Banco de Dados |
| `TailwindCSS` | `3.3.5` | Estilização |
| `Flowbite` | `2.0.0` | Componentes UI |
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

## 🧪 Testes
Para executar a suíte de testes:
```bash
python manage.py test
```

## 🤝 Como Contribuir
Quer contribuir? Ótimo! Leia nosso [Guia de Contribuição](CONTRIBUTING.md) para detalhes sobre nosso código de conduta e o processo de envio de pull requests.

## 📸 Screenshots
![](https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2/raw/main/.gitassets/2.jpg)
![](https://github.com/Prefeitura-Municipal-de-Novo-Horizonte/sisinfo-v2/raw/main/.gitassets/3.jpg)